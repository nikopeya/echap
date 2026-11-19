import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "agent_lock.py"


class AgentLockTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "docs").mkdir()
        for name in ("a.txt", "b.txt", "c.txt"):
            (self.root / "docs" / name).write_text("initial\n", encoding="utf-8")

    def tearDown(self):
        self.tempdir.cleanup()

    def lock(self, *args, check=True, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=cwd or self.root,
            capture_output=True,
            text=True,
            check=check,
        )

    def acquire(self, session, paths, wait="0", check=True):
        return self.lock(
            "acquire", "--session", session, "--task", "ECH-test",
            "--wait", wait, *paths, check=check,
        )

    def test_cycle_and_wrong_token(self):
        first = json.loads(self.acquire("session-a", ["docs/a.txt", "docs/b.txt"]).stdout)
        self.assertEqual(first["status"], "acquired")
        second = self.acquire("session-b", ["docs/b.txt"], check=False)
        self.assertEqual(second.returncode, 1)
        occupied = json.loads(second.stdout)
        self.assertEqual(occupied["owners"][0]["session"], "session-a")
        self.assertEqual(self.lock("release", "--token", "wrong", "docs/a.txt", "docs/b.txt", check=False).returncode, 1)
        self.assertEqual(self.lock("check", "--token", first["token"], "docs/a.txt", "docs/b.txt").returncode, 0)
        self.lock("release", "--token", first["token"], "docs/a.txt", "docs/b.txt")
        self.assertEqual(json.loads(self.lock("status").stdout)["status"], "free")
        self.assertEqual(self.lock("check", "--token", first["token"], "docs/a.txt", check=False).returncode, 1)

    def test_disjoint_files_can_be_reserved_concurrently(self):
        first = json.loads(self.acquire("session-a", ["docs/a.txt"]).stdout)
        second = json.loads(self.acquire("session-b", ["docs/b.txt"]).stdout)
        self.assertNotEqual(first["token"], second["token"])
        self.assertEqual(len(json.loads(self.lock("status").stdout)["locks"]), 2)

    def test_twenty_competing_sessions_have_one_winner(self):
        processes = [
            subprocess.Popen(
                [sys.executable, str(SCRIPT), "acquire", "--session", f"session-{index}",
                 "--task", "ECH-test", "--wait", "0", "docs/a.txt"],
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for index in range(20)
        ]
        results = [process.communicate() for process in processes]
        statuses = [json.loads(stdout)["status"] for stdout, _ in results]
        self.assertEqual(statuses.count("acquired"), 1)
        self.assertEqual(statuses.count("occupied"), 19)
        self.assertTrue(all(not stderr for _, stderr in results))

    def test_concurrent_writes_do_not_lose_updates(self):
        script = (
            "import json,subprocess,sys,pathlib\n"
            "for index in range(12):\n"
            " result=subprocess.run([sys.executable,sys.argv[1],'acquire','--session',sys.argv[2],'--task','ECH-test','--wait','10','shared.txt'],capture_output=True,text=True)\n"
            " assert result.returncode==0,result.stderr\n"
            " token=json.loads(result.stdout)['token']\n"
            " path=pathlib.Path('shared.txt')\n"
            " count=int(path.read_text())+1\n"
            " path.write_text(str(count))\n"
            " subprocess.run([sys.executable,sys.argv[1],'release','--token',token,'shared.txt'],check=True,capture_output=True)\n"
        )
        (self.root / "shared.txt").write_text("0", encoding="utf-8")
        processes = [
            subprocess.Popen(
                [sys.executable, "-c", script, str(SCRIPT), f"writer-{index}"],
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for index in range(4)
        ]
        for process in processes:
            stdout, stderr = process.communicate(timeout=60)
            self.assertEqual(process.returncode, 0, stderr)
        self.assertEqual((self.root / "shared.txt").read_text(encoding="utf-8"), "48")

    def test_recover_requires_matching_owner(self):
        result = self.acquire("old", ["docs/a.txt"])
        token = json.loads(result.stdout)["token"]
        self.assertEqual(self.lock(
            "recover", "--session", "other", "--acquired", "anything",
            "--confirm-stopped", "docs/a.txt", check=False,
        ).returncode, 1)
        self.assertEqual(self.lock("check", "--token", token, "docs/a.txt").returncode, 0)
        status = json.loads(self.lock("status", "docs/a.txt").stdout)
        self.assertEqual(self.lock(
            "recover", "--session", "old", "--acquired", status["locks"][0]["acquired"],
            "--confirm-stopped", "docs/a.txt",
        ).returncode, 0)
        self.assertEqual(json.loads(self.lock("status").stdout)["status"], "free")

    def test_paths_are_confined_to_repository(self):
        for path in ("../outside.txt", str(self.root / "docs/a.txt"), ".git/config", "docs"):
            self.assertEqual(self.acquire("bad", [path], check=False).returncode, 2)
        self.assertEqual(self.acquire("bad", ["New-Name.TXT"], check=False).returncode, 2)
        self.assertEqual(self.lock("status", cwd=self.root / "docs").returncode, 0)

    def test_external_symlink_is_rejected(self):
        outside = self.root.parent / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        (self.root / "docs" / "link.txt").symlink_to(outside)
        self.assertEqual(self.acquire("bad", ["docs/link.txt"], check=False).returncode, 2)

    def test_database_is_private(self):
        self.acquire("session-a", ["docs/a.txt"])
        path = self.root / ".git" / "echap-agent-lock.sqlite3"
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_no_git_repository_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as outside:
            result = self.lock("status", cwd=outside, check=False)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
