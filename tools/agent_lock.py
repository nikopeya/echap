import argparse
import contextlib
import datetime
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import uuid


def git_value(*arguments):
    result = subprocess.run(
        ["git", "rev-parse", *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("Cette commande doit être exécutée dans un arbre de travail Git.")
    return Path(result.stdout.strip())


def connect():
    path = git_value("--path-format=absolute", "--git-common-dir") / "echap-agent-lock.sqlite3"
    previous_umask = os.umask(0o077)
    try:
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(descriptor)
        connection = sqlite3.connect(path, timeout=5, isolation_level=None)
        connection.execute(
            "CREATE TABLE IF NOT EXISTS file_locks "
            "(path TEXT PRIMARY KEY, token TEXT NOT NULL, session TEXT NOT NULL, "
            "task TEXT NOT NULL, acquired TEXT NOT NULL)"
        )
        connection.execute("PRAGMA busy_timeout = 50")
        return connection
    finally:
        os.umask(previous_umask)


def normalize_paths(raw_paths):
    root = git_value("--show-toplevel").resolve(strict=True)
    paths = set()
    for raw_path in raw_paths:
        if not raw_path or not raw_path.isprintable() or "\\" in raw_path:
            raise ValueError(f"Chemin invalide : {raw_path!r}")
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Utiliser un chemin relatif au dépôt, sans parent : {raw_path}")
        candidate = (root / relative).resolve(strict=False)
        try:
            canonical = candidate.relative_to(root).as_posix()
        except ValueError as exc:
            raise ValueError(f"Chemin hors du dépôt : {raw_path}") from exc
        if canonical == ".git" or canonical.startswith(".git/"):
            raise ValueError(f"Les métadonnées Git ne sont pas réservables : {raw_path}")
        if candidate.exists() and candidate.is_dir():
            raise ValueError(f"Le chemin doit désigner un fichier : {raw_path}")
        if not candidate.exists() and (
            not candidate.name.isascii() or candidate.name != candidate.name.lower()
        ):
            raise ValueError(f"Un nouveau nom de fichier doit être en ASCII minuscules : {raw_path}")
        paths.add(canonical)
    return sorted(paths)


def rows(connection, paths):
    return [
        {
            "path": row[0],
            "session": row[1],
            "task": row[2],
            "acquired": row[3],
        }
        for row in connection.execute(
            "SELECT path, session, task, acquired FROM file_locks "
            "WHERE path IN (%s) ORDER BY path" % ",".join("?" * len(paths)),
            paths,
        ).fetchall()
    ]


def begin_write(connection):
    try:
        connection.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError as exc:
        if "locked" not in str(exc).lower():
            raise
        return False
    return True


def acquire(connection, session, task, raw_paths, wait):
    paths = normalize_paths(raw_paths)
    deadline = time.monotonic() + wait
    token = uuid.uuid4().hex
    while True:
        if begin_write(connection):
            try:
                acquired = datetime.datetime.now(datetime.timezone.utc).isoformat()
                connection.executemany(
                    "INSERT INTO file_locks (path, token, session, task, acquired) "
                    "VALUES (?, ?, ?, ?, ?)",
                    [(path, token, session, task, acquired) for path in paths],
                )
            except sqlite3.IntegrityError:
                connection.execute("ROLLBACK")
            else:
                connection.execute("COMMIT")
                print(json.dumps({
                    "status": "acquired",
                    "token": token,
                    "session": session,
                    "paths": paths,
                }, ensure_ascii=False))
                return 0
        if time.monotonic() >= deadline:
            print(json.dumps({
                "status": "occupied",
                "paths": paths,
                "owners": rows(connection, paths),
            }, ensure_ascii=False))
            return 1
        time.sleep(min(0.1, max(0, deadline - time.monotonic())))


def check(connection, token, raw_paths):
    paths = normalize_paths(raw_paths)
    found = connection.execute(
        "SELECT token FROM file_locks WHERE path IN (%s)" % ",".join("?" * len(paths)),
        paths,
    ).fetchall()
    if len(found) != len(paths) or any(row[0] != token for row in found):
        print("Verrou absent ou détenu par une autre session.", file=sys.stderr)
        return 1
    print("Verrou détenu par cette session pour tous les fichiers demandés.")
    return 0


def release(connection, token, raw_paths):
    paths = normalize_paths(raw_paths)
    if not begin_write(connection):
        print("Libération temporairement indisponible ; réessayer.", file=sys.stderr)
        return 2
    found = connection.execute(
        "SELECT token FROM file_locks WHERE path IN (%s)" % ",".join("?" * len(paths)),
        paths,
    ).fetchall()
    if len(found) != len(paths) or any(row[0] != token for row in found):
        connection.execute("ROLLBACK")
        print("Libération refusée : jeton incorrect ou verrou absent.", file=sys.stderr)
        return 1
    connection.execute(
        "DELETE FROM file_locks WHERE path IN (%s)" % ",".join("?" * len(paths)),
        paths,
    )
    connection.execute("COMMIT")
    print(json.dumps({"status": "released", "paths": paths}, ensure_ascii=False))
    return 0


def recover(connection, session, acquired, raw_paths):
    paths = normalize_paths(raw_paths)
    if not begin_write(connection):
        print("Récupération temporairement indisponible ; réessayer.", file=sys.stderr)
        return 2
    found = rows(connection, paths)
    if len(found) != len(paths) or any(
        row["session"] != session or row["acquired"] != acquired for row in found
    ):
        connection.execute("ROLLBACK")
        print("Récupération refusée : propriétaire différent ou verrou absent.", file=sys.stderr)
        return 1
    connection.execute(
        "DELETE FROM file_locks WHERE path IN (%s)" % ",".join("?" * len(paths)),
        paths,
    )
    connection.execute("COMMIT")
    print("Verrou récupéré. Vérifier les modifications avant toute reprise.")
    return 0


def text(value):
    if not value or len(value) > 120 or not value.isprintable():
        raise argparse.ArgumentTypeError("Utiliser un libellé imprimable de 1 à 120 caractères, sans secret.")
    return value


def nonnegative(value):
    try:
        result = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Le délai doit être un entier en secondes.") from exc
    if not 0 <= result <= 3600:
        raise argparse.ArgumentTypeError("Le délai doit être compris entre 0 et 3600 secondes.")
    return result


def main():
    parser = argparse.ArgumentParser(description="Verrous locaux par fichier pour sessions coopérantes.")
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("acquire")
    start.add_argument("--session", required=True, type=text)
    start.add_argument("--task", required=True, type=text)
    start.add_argument("--wait", type=nonnegative, default=60)
    start.add_argument("paths", nargs="+")
    inspect = commands.add_parser("check")
    inspect.add_argument("--token", required=True)
    inspect.add_argument("paths", nargs="+")
    finish = commands.add_parser("release")
    finish.add_argument("--token", required=True)
    finish.add_argument("paths", nargs="+")
    status = commands.add_parser("status")
    status.add_argument("paths", nargs="*")
    restore = commands.add_parser("recover")
    restore.add_argument("--session", required=True, type=text)
    restore.add_argument("--acquired", required=True)
    restore.add_argument("--confirm-stopped", action="store_true", required=True)
    restore.add_argument("paths", nargs="+")
    args = parser.parse_args()
    try:
        with contextlib.closing(connect()) as connection:
            if args.command == "acquire":
                return acquire(connection, args.session, args.task, args.paths, args.wait)
            if args.command == "check":
                return check(connection, args.token, args.paths)
            if args.command == "release":
                return release(connection, args.token, args.paths)
            if args.command == "recover":
                return recover(connection, args.session, args.acquired, args.paths)
            paths = normalize_paths(args.paths) if args.paths else [
                row[0] for row in connection.execute("SELECT path FROM file_locks ORDER BY path")
            ]
            found = rows(connection, paths) if paths else []
            print(json.dumps({
                "status": "occupied" if found else "free",
                "locks": found,
            }, ensure_ascii=False))
            return 0
    except (OSError, RuntimeError, ValueError, sqlite3.Error) as exc:
        print(f"Coordination indisponible : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
