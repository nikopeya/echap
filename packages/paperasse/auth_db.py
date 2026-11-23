"""
Module d'authentification, de persistance et de métriques financières pour ÉCHAP.
Cloisonnement strict par utilisateur et conservation permanente en base de données.
"""

import os
import sqlite3
import hashlib
import secrets
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "echap_mtp.sqlite")

_schema_ready = False
_schema_lock = threading.Lock()


def get_db_connection() -> sqlite3.Connection:
    """
    Retourne une connexion à la base de données persistante.
    Le schéma et les migrations ne sont vérifiés qu'une seule fois par processus,
    afin que chaque requête reste rapide (surtout sur un disque distant).
    """
    global _schema_ready
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout=20000")
    except Exception:
        pass

    if not _schema_ready:
        with _schema_lock:
            if not _schema_ready:
                _init_schema()
                _schema_ready = True
    return conn


def _init_schema() -> None:
    """Crée et migre le schéma de la base (exécuté une seule fois par processus)."""
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except Exception:
        pass
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                company_name TEXT NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                interactive_question TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        # Migration douce si la colonne interactive_question manque
        try:
            conn.execute("ALTER TABLE chat_messages ADD COLUMN interactive_question TEXT DEFAULT NULL")
        except Exception:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                kind TEXT NOT NULL, -- 'upload' ou 'export'
                filename TEXT NOT NULL,
                content_blob BLOB NOT NULL,
                size_kb REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS company_finances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                entity_id INTEGER,
                ca_ytd REAL DEFAULT 0.0,
                ca_month REAL DEFAULT 0.0,
                tresorerie REAL DEFAULT 0.0,
                creances_clients REAL DEFAULT 0.0,
                tva_due REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)
        # Migration company_finances si user_id est encore clé primaire unique
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(company_finances)")
            cols = {r[1]: r for r in cursor.fetchall()}
            if "user_id" in cols and cols["user_id"][5] == 1:
                cursor.execute("ALTER TABLE company_finances RENAME TO company_finances_old")
                cursor.execute("""
                    CREATE TABLE company_finances (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        entity_id INTEGER,
                        ca_ytd REAL DEFAULT 0.0,
                        ca_month REAL DEFAULT 0.0,
                        tresorerie REAL DEFAULT 0.0,
                        creances_clients REAL DEFAULT 0.0,
                        tva_due REAL DEFAULT 0.0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
                    )
                """)
                cursor.execute("""
                    INSERT INTO company_finances (user_id, ca_ytd, ca_month, tresorerie, creances_clients, tva_due, updated_at)
                    SELECT user_id, ca_ytd, ca_month, tresorerie, creances_clients, tva_due, updated_at
                    FROM company_finances_old
                """)
                cursor.execute("DROP TABLE company_finances_old")
        except Exception:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS company_profiles (
                user_id INTEGER PRIMARY KEY,
                legal_form TEXT DEFAULT 'SAS',
                siren TEXT DEFAULT '',
                siret TEXT DEFAULT '',
                address TEXT DEFAULT '',
                postal_code TEXT DEFAULT '',
                city TEXT DEFAULT '',
                activity_code TEXT DEFAULT '',
                activity_label TEXT DEFAULT '',
                regime_tva TEXT DEFAULT 'Réel normal (20%)',
                regime_imposition TEXT DEFAULT 'IS',
                fiscal_year_end TEXT DEFAULT '31/12',
                iban TEXT DEFAULT '',
                bic TEXT DEFAULT '',
                president TEXT DEFAULT '',
                president_role TEXT DEFAULT 'Président',
                onboarding_completed INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        # Migrations douces pour colonnes ajoutées à company_profiles
        for col_def in [
            "activity_label TEXT DEFAULT ''",
            "fiscal_year_end TEXT DEFAULT '31/12'",
            "president_role TEXT DEFAULT 'Président'",
            "onboarding_completed INTEGER DEFAULT 0"
        ]:
            try:
                conn.execute(f"ALTER TABLE company_profiles ADD COLUMN {col_def}")
            except Exception:
                pass

        # Migration users : ajout full_name
        try:
            conn.execute("ALTER TABLE users ADD COLUMN full_name TEXT DEFAULT ''")
        except Exception:
            pass

        # Table des Structures / Entités (indépendante de la personne physique)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                structure_type TEXT NOT NULL DEFAULT 'company', -- 'micro_enterprise', 'company', 'sci', 'liberal'
                legal_form TEXT DEFAULT 'SAS',
                siren TEXT DEFAULT '',
                siret TEXT DEFAULT '',
                address TEXT DEFAULT '',
                postal_code TEXT DEFAULT '',
                city TEXT DEFAULT '',
                activity_code TEXT DEFAULT '',
                activity_label TEXT DEFAULT '',
                regime_tva TEXT DEFAULT 'Réel normal (20%)',
                regime_imposition TEXT DEFAULT 'IS',
                fiscal_year_end TEXT DEFAULT '31/12',
                iban TEXT DEFAULT '',
                bic TEXT DEFAULT '',
                representative_name TEXT DEFAULT '',
                representative_role TEXT DEFAULT 'Dirigeant',
                onboarding_completed INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table d'association N:M : Utilisateurs ⇄ Structures
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memberships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entity_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'owner', -- 'owner', 'admin', 'collaborator', 'accountant', 'viewer'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, entity_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)

        # Ajout colonne entity_id sur les tables métier pour cloisonnement par structure
        for tbl in ["chat_messages", "documents", "company_finances", "company_deadlines"]:
            try:
                conn.execute(f"ALTER TABLE {tbl} ADD COLUMN entity_id INTEGER DEFAULT NULL")
            except Exception:
                pass

        # Migration automatique transparente des profils existants vers entities + memberships
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, company_name, full_name FROM users")
            existing_users = cursor.fetchall()
            for u in existing_users:
                uid = u["id"]
                cursor.execute("SELECT entity_id FROM memberships WHERE user_id = ?", (uid,))
                m_row = cursor.fetchone()
                if not m_row:
                    cursor.execute("SELECT * FROM company_profiles WHERE user_id = ?", (uid,))
                    p_row = cursor.fetchone()
                    # Si ni profil ni company_name défini, c'est un nouvel utilisateur sans structure : ne rien créer
                    if not p_row and not (u["company_name"] and u["company_name"].strip()):
                        continue

                    ent_name = u["company_name"] or "Mon Entreprise"
                    form = "SAS"
                    siren, siret, addr, cp, city = "", "", "", "", ""
                    ape, act_lbl = "", ""
                    tva, imp, fye = "Réel normal (20%)", "IS", "31/12"
                    iban, bic = "", ""
                    rep_name = u["full_name"] or ""
                    rep_role = "Dirigeant"
                    ob_done = 0
                    stype = "company"

                    if p_row:
                        keys = p_row.keys()
                        form = p_row["legal_form"] or "SAS"
                        siren = p_row["siren"] or ""
                        siret = p_row["siret"] or ""
                        addr = p_row["address"] or ""
                        cp = p_row["postal_code"] or ""
                        city = p_row["city"] or ""
                        ape = p_row["activity_code"] or ""
                        act_lbl = p_row["activity_label"] if "activity_label" in keys else ""
                        tva = p_row["regime_tva"] or "Réel normal (20%)"
                        imp = p_row["regime_imposition"] or "IS"
                        fye = p_row["fiscal_year_end"] if "fiscal_year_end" in keys else "31/12"
                        iban = p_row["iban"] or ""
                        bic = p_row["bic"] or ""
                        rep_name = p_row["president"] or rep_name
                        rep_role = p_row["president_role"] if "president_role" in keys else "Dirigeant"
                        ob_done = p_row["onboarding_completed"] if "onboarding_completed" in keys else 0

                    if "Micro" in form or "Auto" in form or "Individuelle" in form:
                        stype = "micro_enterprise"
                    elif "SCI" in form:
                        stype = "sci"
                    elif "BNC" in form or "libérale" in form.lower():
                        stype = "liberal"

                    cursor.execute("""
                        INSERT INTO entities (
                            name, structure_type, legal_form, siren, siret,
                            address, postal_code, city, activity_code, activity_label,
                            regime_tva, regime_imposition, fiscal_year_end, iban, bic,
                            representative_name, representative_role, onboarding_completed
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ent_name, stype, form, siren, siret,
                        addr, cp, city, ape, act_lbl,
                        tva, imp, fye, iban, bic,
                        rep_name, rep_role, ob_done
                    ))
                    new_ent_id = cursor.lastrowid
                    cursor.execute(
                        "INSERT OR IGNORE INTO memberships (user_id, entity_id, role) VALUES (?, ?, 'owner')",
                        (uid, new_ent_id)
                    )
                    cursor.execute("UPDATE chat_messages SET entity_id = ? WHERE user_id = ? AND entity_id IS NULL", (new_ent_id, uid))
                    cursor.execute("UPDATE documents SET entity_id = ? WHERE user_id = ? AND entity_id IS NULL", (new_ent_id, uid))
                    cursor.execute("UPDATE company_deadlines SET entity_id = ? WHERE user_id = ? AND entity_id IS NULL", (new_ent_id, uid))
                    cursor.execute("UPDATE company_finances SET entity_id = ? WHERE user_id = ? AND entity_id IS NULL", (new_ent_id, uid))
        except Exception as e:
            print(f"[MIGRATION ERROR] {e}")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS company_deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entity_id INTEGER DEFAULT NULL,
                label TEXT NOT NULL,
                date TEXT NOT NULL,
                urgency TEXT NOT NULL,
                statut TEXT NOT NULL,
                montant TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
    conn.close()


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return salt, hashed


def register_user(username: str, password_or_company: str, password: Optional[str] = None, full_name: str = "") -> Dict[str, Any]:
    """
    Crée un compte utilisateur (personne physique).
    Supporte la nouvelle signature : register_user(username, password, full_name)
    et l'ancienne signature : register_user(username, company_name, password).
    Aucun nom d'entreprise n'est obligatoire à l'inscription !
    """
    clean_username = username.strip().lower()
    if not clean_username:
        return {"error": "Identifiant requis."}

    # Détection de l'ordre des arguments (rétrocompatibilité)
    if password is not None:
        # Ancienne signature : (username, company_name, password)
        comp_name = password_or_company.strip()
        pwd = password
        name = full_name.strip() or comp_name
    else:
        # Nouvelle signature : (username, password, full_name)
        pwd = password_or_company
        comp_name = ""
        name = full_name.strip()

    if not pwd:
        return {"error": "Mot de passe requis."}

    salt, p_hash = hash_password(pwd)

    conn = None
    try:
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, full_name, company_name, salt, password_hash) VALUES (?, ?, ?, ?, ?)",
                (clean_username, name, comp_name, salt, p_hash)
            )
            user_id = cursor.lastrowid

            # Si un nom d'entreprise a été spécifié (comptes démo), créer l'entité
            if comp_name:
                cursor.execute("""
                    INSERT INTO entities (name, structure_type, legal_form, representative_name, onboarding_completed)
                    VALUES (?, 'company', 'SAS', ?, 0)
                """, (comp_name, name or clean_username))
                ent_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO memberships (user_id, entity_id, role) VALUES (?, ?, 'owner')",
                    (user_id, ent_id)
                )

            return {
                "id": user_id,
                "username": clean_username,
                "full_name": name,
                "company_name": comp_name
            }
    except sqlite3.IntegrityError:
        return {"error": f"L'identifiant « {clean_username} » est déjà utilisé."}
    except Exception as e:
        return {"error": f"Erreur lors de la création : {e}"}
    finally:
        if conn:
            conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Vérifie les accès d'un utilisateur et retourne son profil et sa structure active."""
    clean_username = username.strip().lower()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, full_name, company_name, salt, password_hash FROM users WHERE username = ?",
            (clean_username,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        salt = row["salt"]
        expected_hash = row["password_hash"]
        _, actual_hash = hash_password(password, salt=salt)

        if actual_hash == expected_hash:
            # Récupérer l'entité active
            cursor.execute("""
                SELECT e.id, e.name, e.structure_type, e.legal_form, e.onboarding_completed, m.role
                FROM entities e
                JOIN memberships m ON e.id = m.entity_id
                WHERE m.user_id = ?
                ORDER BY e.id ASC LIMIT 1
            """, (row["id"],))
            active_ent = cursor.fetchone()
            comp_display = active_ent["name"] if active_ent else (row["company_name"] or "")

            return {
                "id": row["id"],
                "username": row["username"],
                "full_name": row["full_name"] if "full_name" in row.keys() and row["full_name"] else row["username"],
                "company_name": comp_display,
                "active_entity_id": active_ent["id"] if active_ent else None
            }
        return None
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return None
    finally:
        if conn:
            conn.close()


def seed_default_testers():
    """Comptes de démarrage disponibles avec profils pré-configurés."""
    default_accounts = [
        ("testeur1", "ACME Solutions SAS", "test1234"),
        ("testeur2", "Martin Conseil (EI)", "test1234"),
        ("testeur3", "SCI Pierre & Patrimoine", "test1234")
    ]
    for username, company, pwd in default_accounts:
        register_user(username, company, pwd)

    # Initialiser les profils complets par défaut pour les testeurs démo s'ils n'existent pas
    demo_profiles = {
        1: {
            "legal_form": "SAS",
            "siren": "888123456",
            "siret": "88812345600018",
            "address": "12 rue de la Paix",
            "postal_code": "75002",
            "city": "Paris",
            "activity_code": "62.01Z",
            "activity_label": "Programmation informatique et conseil logiciel",
            "regime_tva": "Réel normal (20%)",
            "regime_imposition": "IS",
            "fiscal_year_end": "31/12",
            "iban": "FR7630006000011234567890189",
            "bic": "BNPAFRPPXXX",
            "president": "Alexandre Martin",
            "president_role": "Président",
            "onboarding_completed": 1
        },
        2: {
            "legal_form": "Micro-entreprise",
            "siren": "777987654",
            "siret": "77798765400012",
            "address": "5 avenue Victor Hugo",
            "postal_code": "69002",
            "city": "Lyon",
            "activity_code": "70.22Z",
            "activity_label": "Conseil pour les affaires et gestion",
            "regime_tva": "Franchise en base de TVA (art. 293 B)",
            "regime_imposition": "IR",
            "fiscal_year_end": "31/12",
            "iban": "FR7610058000019876543210145",
            "bic": "SGFRFRPPXXX",
            "president": "Sophie Martin",
            "president_role": "Entrepreneur individuel",
            "onboarding_completed": 1
        },
        3: {
            "legal_form": "SCI",
            "siren": "666456789",
            "siret": "66645678900015",
            "address": "8 place Bellecour",
            "postal_code": "69002",
            "city": "Lyon",
            "activity_code": "68.20B",
            "activity_label": "Location de terrains et autres biens immobiliers",
            "regime_tva": "Réel normal (20%)",
            "regime_imposition": "IS",
            "fiscal_year_end": "31/12",
            "iban": "FR7630004000016549873210190",
            "bic": "BNPAFRPPXXX",
            "president": "Pierre Durand",
            "president_role": "Gérant",
            "onboarding_completed": 1
        }
    }
    for uid, prof in demo_profiles.items():
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT onboarding_completed FROM company_profiles WHERE user_id = ?", (uid,))
            existing = cursor.fetchone()
            if not existing:
                update_company_profile(uid, prof)
        except Exception:
            pass
        finally:
            if conn:
                conn.close()


# --- CONVERSATIONS PERSISTANTES ---

def load_user_chat(user_id: int, entity_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Récupère l'historique complet des messages pour cet utilisateur et cette structure."""
    conn = None
    messages = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if entity_id:
            cursor.execute(
                "SELECT role, content, interactive_question FROM chat_messages WHERE entity_id = ? ORDER BY id ASC",
                (entity_id,)
            )
        else:
            cursor.execute(
                "SELECT role, content, interactive_question FROM chat_messages WHERE user_id = ? ORDER BY id ASC",
                (user_id,)
            )
        rows = cursor.fetchall()
        for r in rows:
            q_data = None
            if r["interactive_question"]:
                try:
                    q_data = json.loads(r["interactive_question"])
                except Exception:
                    pass
            messages.append({"role": r["role"], "content": r["content"], "question_data": q_data})
    except Exception as e:
        print(f"[CHAT LOAD ERROR] {e}")
    finally:
        if conn:
            conn.close()
    return messages


def save_user_message(user_id: int, role: str, content: str, question_data: Optional[Dict[str, Any]] = None, entity_id: Optional[int] = None):
    """Enregistre un message en base avec support éventuel d'une question interactive et d'une entité."""
    conn = None
    try:
        conn = get_db_connection()
        q_json = json.dumps(question_data, ensure_ascii=False) if question_data else None
        with conn:
            conn.execute(
                "INSERT INTO chat_messages (user_id, entity_id, role, content, interactive_question) VALUES (?, ?, ?, ?, ?)",
                (user_id, entity_id, role, content, q_json)
            )
    except Exception as e:
        print(f"[CHAT SAVE ERROR] {e}")
    finally:
        if conn:
            conn.close()


def clear_user_chat(user_id: int, entity_id: Optional[int] = None):
    """Efface la conversation."""
    conn = None
    try:
        conn = get_db_connection()
        with conn:
            if entity_id:
                conn.execute("DELETE FROM chat_messages WHERE entity_id = ?", (entity_id,))
            else:
                conn.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
    except Exception as e:
        print(f"[CHAT CLEAR ERROR] {e}")
    finally:
        if conn:
            conn.close()


# --- SUIVI FINANCIER & COMPTABLE EN TEMPS RÉEL ---

def get_company_finances(user_id: int, entity_id: Optional[int] = None) -> Dict[str, Any]:
    """Retourne les indicateurs financiers de l'entreprise ou structure."""
    conn = None
    finances = {
        "ca_ytd": 0.0,
        "ca_month": 0.0,
        "tresorerie": 0.0,
        "creances_clients": 0.0,
        "tva_due": 0.0,
        "recent_transactions": [],
        "echeances": []
    }
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if entity_id:
            cursor.execute(
                "SELECT ca_ytd, ca_month, tresorerie, creances_clients, tva_due FROM company_finances WHERE entity_id = ?",
                (entity_id,)
            )
        else:
            cursor.execute(
                "SELECT ca_ytd, ca_month, tresorerie, creances_clients, tva_due FROM company_finances WHERE user_id = ?",
                (user_id,)
            )
        row = cursor.fetchone()
        if row:
            finances["ca_ytd"] = row["ca_ytd"]
            finances["ca_month"] = row["ca_month"]
            finances["tresorerie"] = row["tresorerie"]
            finances["creances_clients"] = row["creances_clients"]
            finances["tva_due"] = row["tva_due"]

        # Récupération des échéances réelles enregistrées en base
        if entity_id:
            cursor.execute(
                "SELECT label, date, urgency, statut, montant FROM company_deadlines WHERE entity_id = ? ORDER BY id ASC",
                (entity_id,)
            )
        else:
            cursor.execute(
                "SELECT label, date, urgency, statut, montant FROM company_deadlines WHERE user_id = ? ORDER BY id ASC",
                (user_id,)
            )
        db_deadlines = cursor.fetchall()
        if db_deadlines:
            finances["echeances"] = [
                {"label": r["label"], "date": r["date"], "urgency": r["urgency"], "statut": r["statut"], "montant": r["montant"]}
                for r in db_deadlines
            ]
    except Exception as e:
        print(f"[FINANCES ERROR] {e}")
    finally:
        if conn:
            conn.close()

    # Données d'exemple uniquement pour le compte de démonstration n°1 (testeur1) si aucune échéance n'est en base
    if user_id == 1 and not entity_id:
        finances["recent_transactions"] = [
            {"date": "16/11/2026", "label": "Virement Client Alpha", "amount": 2400.0, "type": "credit", "compte": "411100"},
            {"date": "14/11/2026", "label": "Abonnement Logiciel SaaS", "amount": -89.0, "type": "debit", "compte": "651000"},
            {"date": "10/11/2026", "label": "Virement Client Beta", "amount": 1800.0, "type": "credit", "compte": "411100"},
            {"date": "05/11/2026", "label": "Prélèvement Télécom Fibre", "amount": -45.0, "type": "debit", "compte": "626000"},
            {"date": "02/11/2026", "label": "Frais bancaires de tenue de compte", "amount": -18.0, "type": "debit", "compte": "627000"},
        ]
        if not finances["echeances"]:
            finances["echeances"] = [
                {"date": "19/11/2026", "label": "Télédéclaration TVA CA3 (Octobre)", "urgency": "Urgent", "statut": "À valider", "montant": f"{finances['tva_due']:,.0f} €"},
                {"date": "30/11/2026", "label": "Clôture mensuelle & Rapprochement bancaire", "urgency": "À venir", "statut": "En attente", "montant": "-"},
                {"date": "15/12/2026", "label": "Cotisation Foncière des Entreprises (CFE)", "urgency": "À venir", "statut": "Prévu", "montant": "640 €"},
                {"date": "05/01/2027", "label": "Déclaration sociale URSSAF (Trimestre 4)", "urgency": "À venir", "statut": "Prévu", "montant": "2 150 €"}
            ]

    return finances

    return finances


# --- GESTION DES DOCUMENTS ET PIÈCES (BLOBS) ---

def save_document(user_id: int, filename: str, content_bytes: bytes, kind: str = "upload") -> Dict[str, Any]:
    """Enregistre un document en base binaire."""
    size_kb = round(len(content_bytes) / 1024, 1)
    conn = None
    try:
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO documents (user_id, kind, filename, content_blob, size_kb) VALUES (?, ?, ?, ?, ?)",
                (user_id, kind, filename, content_bytes, size_kb)
            )
            doc_id = cursor.lastrowid
            return {"id": doc_id, "filename": filename, "size_kb": size_kb}
    except Exception as e:
        print(f"[DOC SAVE ERROR] {e}")
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()


def list_user_documents(user_id: int, kind: str = "upload") -> List[Dict[str, Any]]:
    """Liste les documents pour un utilisateur."""
    conn = None
    docs = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, filename, size_kb, created_at FROM documents WHERE user_id = ? AND kind = ? ORDER BY id DESC",
            (user_id, kind)
        )
        rows = cursor.fetchall()
        for r in rows:
            docs.append({
                "id": r["id"],
                "filename": r["filename"],
                "size_kb": r["size_kb"],
                "created_at": r["created_at"]
            })
    except Exception as e:
        print(f"[DOC LIST ERROR] {e}")
    finally:
        if conn:
            conn.close()
    return docs


def create_and_record_invoice(user_id: int, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """Génère le document officiel de facture, l'enregistre en base de données et actualise le tableau de bord financier."""
    import re
    conn = get_db_connection()
    today_str = datetime.now().strftime("%d/%m/%Y")

    # 1. Numérotation séquentielle par utilisateur
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM documents WHERE user_id = ? AND (filename LIKE 'FAC-%' OR kind = 'facture')",
        (user_id,)
    )
    count = cursor.fetchone()[0] or 0
    num = f"FAC-2026-{count + 1:03d}"

    # 2. Données financières
    montant_ht = float(invoice_data.get("montant_ht", 0.0))
    taux_tva = float(invoice_data.get("taux_tva", 0.20))
    montant_tva = round(montant_ht * taux_tva, 2)
    montant_ttc = round(montant_ht + montant_tva, 2)

    client_nom = invoice_data.get("client_nom", "Client")
    client_siret = invoice_data.get("client_siret", "Non renseigné")
    client_adresse = invoice_data.get("client_adresse", "Non renseignée")
    description = invoice_data.get("description_prestation", "Prestation de services")
    delai = invoice_data.get("delai_paiement", "30 jours fin de mois")

    # Profil émetteur
    prof = get_company_profile(user_id)
    cursor.execute("SELECT company_name FROM users WHERE id = ?", (user_id,))
    u_row = cursor.fetchone()
    c_name = u_row["company_name"] if u_row else "Votre Entreprise"

    # 3. Rédaction du document Markdown officiel
    content_md = f"""# FACTURE N° {num}

**Date d'émission** : {today_str}  
**Date d'échéance** : {delai}  

---

### Émetteur (Prestataire)
**{c_name}** ({prof.get('legal_form', 'SAS')})  
* **SIRET** : {prof.get('siret', 'Non renseigné')}  
* **Adresse** : {prof.get('address', '')} {prof.get('postal_code', '')} {prof.get('city', '')}  
* **TVA intracommunautaire** : FRXX{prof.get('siren', '')}  

### Client (Destinataire)
**{client_nom}**  
* **SIRET** : {client_siret}  
* **Adresse** : {client_adresse}  

---

### Détail des prestations

| Désignation | Quantité | Prix Unit. HT | Montant HT |
| :--- | :--- | :--- | :--- |
| {description} | 1 | {montant_ht:,.2f} € | {montant_ht:,.2f} € |

---

### Récapitulatif financier

* **Total Hors Taxes (HT)** : {montant_ht:,.2f} €  
* **TVA ({taux_tva*100:.0f} %)** : {montant_tva:,.2f} €  
* **NET À PAYER (TTC)** : **{montant_ttc:,.2f} €**  

---

### Modalités de règlement
* Règlement par virement bancaire sur l'IBAN : `{prof.get('iban', '[IBAN à renseigner]')}` (BIC : `{prof.get('bic', '')}`)  
* Date limite de paiement : {delai}  

### Mentions légales obligatoires
* En cas de retard de paiement, une pénalité égale à trois fois le taux d'intérêt légal sera exigible de plein droit (art. L. 441-10 du Code de commerce).  
* Une indemnité forfaitaire de 40 € pour frais de recouvrement sera due pour toute facture payée après l'échéance (art. D. 441-5 du Code de commerce).  
"""
    file_bytes = content_md.encode("utf-8")
    safe_client = re.sub(r"[^a-zA-Z0-9]", "_", client_nom.split()[0]).lower() or "client"
    filename = f"{num}_{safe_client}.md"
    size_kb = round(len(file_bytes) / 1024, 1)

    # 4. Enregistrement du document dans les exports téléchargeables
    cursor.execute(
        "INSERT INTO documents (user_id, kind, filename, content_blob, size_kb) VALUES (?, 'export', ?, ?, ?)",
        (user_id, filename, file_bytes, size_kb)
    )

    # 5. Actualisation des finances (créances clients + tva due)
    cursor.execute(
        "UPDATE company_finances SET creances_clients = creances_clients + ?, tva_due = tva_due + ? WHERE user_id = ?",
        (montant_ttc, montant_tva, user_id)
    )

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "numero_facture": num,
        "filename": filename,
        "total_ht": montant_ht,
        "total_ttc": montant_ttc,
        "client": client_nom,
        "message": f"Facture {num} enregistrée avec succès. Le document est disponible dans « Documents & Factures » et le tableau de bord a été actualisé (+{montant_ttc:,.2f} € de créances clients)."
    }


def get_document_content(user_id: int, doc_id: int) -> Optional[tuple[str, bytes]]:
    """Récupère le contenu d'un document pour téléchargement."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT filename, content_blob FROM documents WHERE id = ? AND user_id = ?",
            (doc_id, user_id)
        )
        row = cursor.fetchone()
        if row:
            return row["filename"], row["content_blob"]
        return None
    except Exception as e:
        print(f"[DOC GET ERROR] {e}")
# --- STRUCTURES / ENTITÉS & MULTI-ENTITÉS ---

def get_user_entities(user_id: int) -> List[Dict[str, Any]]:
    """Retourne la liste de toutes les structures (sociétés, micro-entreprises, SCI) associées à l'utilisateur."""
    conn = None
    entities = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.name, e.structure_type, e.legal_form, e.siren, e.siret,
                   e.activity_code, e.activity_label, e.regime_tva, e.regime_imposition,
                   e.fiscal_year_end, e.representative_name, e.representative_role,
                   e.onboarding_completed, m.role
            FROM entities e
            JOIN memberships m ON e.id = m.entity_id
            WHERE m.user_id = ?
            ORDER BY e.id ASC
        """, (user_id,))
        rows = cursor.fetchall()
        for r in rows:
            entities.append(dict(r))
    except Exception as e:
        print(f"[GET USER ENTITIES ERROR] {e}")
    finally:
        if conn:
            conn.close()
    return entities


def get_entity_profile(entity_id: int) -> Dict[str, Any]:
    """Retourne la fiche complète d'une entité/structure par son ID."""
    conn = None
    default_profile = {
        "id": entity_id,
        "name": "",
        "company_name": "",
        "structure_type": "company",
        "legal_form": "SAS",
        "siren": "",
        "siret": "",
        "address": "",
        "postal_code": "",
        "city": "",
        "activity_code": "",
        "activity_label": "",
        "regime_tva": "Réel normal (20%)",
        "regime_imposition": "IS",
        "fiscal_year_end": "31/12",
        "iban": "",
        "bic": "",
        "president": "",
        "representative_name": "",
        "president_role": "Dirigeant",
        "representative_role": "Dirigeant",
        "onboarding_completed": 0
    }
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        if row:
            for k in row.keys():
                default_profile[k] = row[k]
            default_profile["company_name"] = row["name"]
            default_profile["president"] = row["representative_name"]
            default_profile["president_role"] = row["representative_role"]
    except Exception as e:
        print(f"[GET ENTITY ERROR] {e}")
    finally:
        if conn:
            conn.close()
    return default_profile


def create_entity_for_user(user_id: int, entity_data: Dict[str, Any], role: str = "owner") -> Dict[str, Any]:
    """Crée une nouvelle entité / structure et l'associe à l'utilisateur."""
    conn = None
    try:
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            stype = entity_data.get("structure_type", "company")
            form = entity_data.get("legal_form", "SAS")
            rep_name = entity_data.get("representative_name") or entity_data.get("president", "").strip()
            rep_role = entity_data.get("representative_role") or entity_data.get("president_role", "Dirigeant")

            # Gestion automatique de la dénomination pour les micro-entreprises / indépendants
            raw_name = entity_data.get("name") or entity_data.get("company_name", "").strip()
            if not raw_name:
                if stype == "micro_enterprise" or "micro" in form.lower():
                    raw_name = f"{rep_name} (Micro-entreprise)" if rep_name else "Mon Activité Indépendante"
                else:
                    raw_name = f"Entreprise {rep_name}" if rep_name else "Nouvelle Société"

            siren = entity_data.get("siren", "").strip()
            siret = entity_data.get("siret", "").strip()
            addr = entity_data.get("address", "").strip()
            cp = entity_data.get("postal_code", "").strip()
            city = entity_data.get("city", "").strip()
            ape = entity_data.get("activity_code", "").strip()
            act_lbl = entity_data.get("activity_label", "").strip()
            tva = entity_data.get("regime_tva", "Réel normal (20%)")
            imp = entity_data.get("regime_imposition", "IS")
            fye = entity_data.get("fiscal_year_end", "31/12")
            iban = entity_data.get("iban", "").strip()
            bic = entity_data.get("bic", "").strip()
            ob_done = entity_data.get("onboarding_completed", 1)

            cursor.execute("""
                INSERT INTO entities (
                    name, structure_type, legal_form, siren, siret,
                    address, postal_code, city, activity_code, activity_label,
                    regime_tva, regime_imposition, fiscal_year_end, iban, bic,
                    representative_name, representative_role, onboarding_completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                raw_name, stype, form, siren, siret,
                addr, cp, city, ape, act_lbl,
                tva, imp, fye, iban, bic,
                rep_name, rep_role, ob_done
            ))
            entity_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO memberships (user_id, entity_id, role) VALUES (?, ?, ?)",
                (user_id, entity_id, role)
            )

            # Finances initiales
            cursor.execute("""
                INSERT INTO company_finances (user_id, entity_id, ca_ytd, ca_month, tresorerie, creances_clients, tva_due)
                VALUES (?, ?, 0.0, 0.0, 0.0, 0.0, 0.0)
            """, (user_id, entity_id))

            # Échéances adaptées à la structure
            deadlines = []
            if "Réel normal" in tva:
                deadlines.append(("Télédéclaration TVA CA3 (Mois précédent)", "19/12/2026", "Urgent", "À valider", "Selon CA"))
            elif "Réel simplifié" in tva:
                deadlines.append(("Acompte semestriel TVA (Formulaire 3514)", "15/07/2027", "À venir", "Prévu", "Selon CA N-1"))
            else:
                deadlines.append(("Franchise en base de TVA (art. 293 B CGI)", "Permanente", "À jour", "Exonéré", "0 € (Pas de déclaration mensuelle)"))

            deadlines.append(("Cotisation Foncière des Entreprises (CFE)", "15/12/2026", "À venir", "Prévu", "Avis à recevoir"))

            if stype == "micro_enterprise" or "micro" in form.lower() or "auto" in form.lower():
                deadlines.append(("Déclaration CA URSSAF (Micro-entreprise)", "31/12/2026", "Urgent", "À déclarer", "Selon recettes"))
            else:
                liasse_date = "15/05/2027" if fye == "31/12" else f"3 mois après le {fye}"
                deadlines.append((f"Clôture d'exercice ({fye}) & Liasse fiscale", liasse_date, "À venir", "Prévu", "Bilan annuel"))

            for lbl, d_date, urg, stat, mnt in deadlines:
                cursor.execute("""
                    INSERT INTO company_deadlines (user_id, entity_id, label, date, urgency, statut, montant)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, entity_id, lbl, d_date, urg, stat, mnt))

            # Message de bienvenue contextualisé sans emoji
            welcome_msg = (
                f"Bonjour **{rep_name or 'entrepreneur'}**.\n\n"
                f"Votre espace pour **{raw_name}** ({form}) est prêt et configuré.\n\n"
                f"**Fiche légale enregistrée :**\n"
                f"- **Structure :** {raw_name} {f'(SIREN {siren})' if siren else ''}\n"
                f"- **Régime fiscal :** {tva} • Imposition {imp} • Clôture au {fye}\n"
                f"- **Représentant légal :** {rep_name or 'Non spécifié'} ({rep_role})\n\n"
                f"Je dispose de toutes les données de cette structure pour votre facturation conforme, votre calendrier fiscal et vos démarches administratives.\n\n"
                f"Que souhaitez-vous traiter ?"
            )
            cursor.execute(
                "INSERT INTO chat_messages (user_id, entity_id, role, content) VALUES (?, ?, 'assistant', ?)",
                (user_id, entity_id, welcome_msg)
            )

            # Rétrocompatibilité : mettre à jour le company_name de users si vide
            cursor.execute("UPDATE users SET company_name = ? WHERE id = ? AND (company_name IS NULL OR company_name = '')", (raw_name, user_id))

            return {"id": entity_id, "name": raw_name, "success": True}
    except Exception as e:
        print(f"[CREATE ENTITY ERROR] {e}")
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()


def update_entity_profile(entity_id: int, profile_data: Dict[str, Any]):
    """Met à jour les informations d'une structure donnée."""
    conn = None
    try:
        conn = get_db_connection()
        with conn:
            name = profile_data.get("name") or profile_data.get("company_name", "")
            rep_name = profile_data.get("representative_name") or profile_data.get("president", "")
            rep_role = profile_data.get("representative_role") or profile_data.get("president_role", "Dirigeant")
            stype = profile_data.get("structure_type", "company")
            ob_comp = profile_data.get("onboarding_completed")
            legal_form = profile_data.get("legal_form", "SAS")
            tva = profile_data.get("regime_tva", "Réel normal (20%)")
            imp = profile_data.get("regime_imposition", "IS")
            fye = profile_data.get("fiscal_year_end", "31/12")

            conn.execute("""
                UPDATE entities SET
                    name = COALESCE(NULLIF(?, ''), name),
                    structure_type = COALESCE(NULLIF(?, ''), structure_type),
                    legal_form = ?,
                    siren = ?,
                    siret = ?,
                    address = ?,
                    postal_code = ?,
                    city = ?,
                    activity_code = ?,
                    activity_label = ?,
                    regime_tva = ?,
                    regime_imposition = ?,
                    fiscal_year_end = ?,
                    iban = ?,
                    bic = ?,
                    representative_name = ?,
                    representative_role = ?,
                    onboarding_completed = COALESCE(?, onboarding_completed),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                name, stype,
                legal_form,
                profile_data.get("siren", ""),
                profile_data.get("siret", ""),
                profile_data.get("address", ""),
                profile_data.get("postal_code", ""),
                profile_data.get("city", ""),
                profile_data.get("activity_code", ""),
                profile_data.get("activity_label", ""),
                tva,
                imp,
                fye,
                profile_data.get("iban", ""),
                profile_data.get("bic", ""),
                rep_name, rep_role,
                ob_comp,
                entity_id
            ))

            # Mise à jour des échéances de la structure
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM memberships WHERE entity_id = ? AND role = 'owner' LIMIT 1", (entity_id,))
            m_row = cursor.fetchone()
            owner_uid = m_row["user_id"] if m_row else None

            if owner_uid:
                cursor.execute("DELETE FROM company_deadlines WHERE entity_id = ?", (entity_id,))
                deadlines = []
                if "Réel normal" in tva:
                    deadlines.append(("Télédéclaration TVA CA3 (Mois précédent)", "19/12/2026", "Urgent", "À valider", "Selon CA"))
                elif "Réel simplifié" in tva:
                    deadlines.append(("Acompte semestriel TVA (Formulaire 3514)", "15/07/2027", "À venir", "Prévu", "Selon CA N-1"))
                else:
                    deadlines.append(("Franchise en base de TVA (art. 293 B CGI)", "Permanente", "À jour", "Exonéré", "0 € (Pas de déclaration mensuelle)"))

                deadlines.append(("Cotisation Foncière des Entreprises (CFE)", "15/12/2026", "À venir", "Prévu", "Avis à recevoir"))

                if stype == "micro_enterprise" or "micro" in legal_form.lower() or "auto" in legal_form.lower():
                    deadlines.append(("Déclaration CA URSSAF (Micro-entreprise)", "31/12/2026", "Urgent", "À déclarer", "Selon recettes"))
                else:
                    liasse_date = "15/05/2027" if fye == "31/12" else f"3 mois après le {fye}"
                    deadlines.append((f"Clôture d'exercice ({fye}) & Liasse fiscale", liasse_date, "À venir", "Prévu", "Bilan annuel"))

                for lbl, d_date, urg, stat, mnt in deadlines:
                    cursor.execute("""
                        INSERT INTO company_deadlines (user_id, entity_id, label, date, urgency, statut, montant)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (owner_uid, entity_id, lbl, d_date, urg, stat, mnt))
    except Exception as e:
        print(f"[UPDATE ENTITY ERROR] {e}")
    finally:
        if conn:
            conn.close()


# --- WRAPPERS DE COMPATIBILITÉ PROFILS & ONBOARDING ---

def get_company_profile(user_id: int, entity_id: Optional[int] = None) -> Dict[str, Any]:
    """Retourne la fiche complète de la structure courante (soit par entity_id, soit la première de l'utilisateur)."""
    if entity_id:
        return get_entity_profile(entity_id)

    # Récupérer l'entité active depuis memberships
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id FROM entities e
            JOIN memberships m ON e.id = m.entity_id
            WHERE m.user_id = ?
            ORDER BY e.id ASC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return get_entity_profile(row["id"])
    except Exception:
        pass
    finally:
        if conn:
            conn.close()

    # Repli rétrocompatible
    default_profile = {
        "legal_form": "SAS",
        "siren": "",
        "siret": "",
        "address": "",
        "postal_code": "",
        "city": "",
        "activity_code": "",
        "activity_label": "",
        "regime_tva": "Réel normal (20%)",
        "regime_imposition": "IS",
        "fiscal_year_end": "31/12",
        "iban": "",
        "bic": "",
        "president": "",
        "president_role": "Président",
        "onboarding_completed": 0
    }
    return default_profile


def update_company_profile(user_id: int, profile_data: Dict[str, Any], entity_id: Optional[int] = None):
    """Met à jour la fiche de l'entité concernée."""
    if entity_id:
        update_entity_profile(entity_id, profile_data)
        return

    # Trouver l'entité de l'utilisateur
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT entity_id FROM memberships WHERE user_id = ? ORDER BY entity_id ASC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        if row:
            update_entity_profile(row["entity_id"], profile_data)
            return
    except Exception:
        pass
    finally:
        if conn:
            conn.close()

    # Si aucune entité n'existe encore, en créer une
    create_entity_for_user(user_id, profile_data)


def is_onboarding_completed(user_id: int, entity_id: Optional[int] = None) -> bool:
    """Vérifie si l'utilisateur a au moins une structure qualifiée et prête."""
    if entity_id:
        ent = get_entity_profile(entity_id)
        return ent.get("onboarding_completed") == 1

    entities = get_user_entities(user_id)
    if not entities:
        return False
    return any(e.get("onboarding_completed") == 1 for e in entities)


def complete_onboarding(user_id: int, profile_data: Dict[str, Any], entity_id: Optional[int] = None) -> Dict[str, Any]:
    """Finalise l'onboarding en créant ou actualisant l'entité de l'utilisateur."""
    profile_data["onboarding_completed"] = 1
    target_ent_id = entity_id
    if not target_ent_id:
        entities = get_user_entities(user_id)
        if entities:
            target_ent_id = entities[0]["id"]
            update_entity_profile(target_ent_id, profile_data)
        else:
            return create_entity_for_user(user_id, profile_data, role="owner")
    else:
        update_entity_profile(target_ent_id, profile_data)

    # Initialiser le message de bienvenue sans emoji si aucun message n'existe
    chat = load_user_chat(user_id, entity_id=target_ent_id)
    if not chat:
        comp = profile_data.get("company_name") or profile_data.get("name", "votre entreprise")
        pres = profile_data.get("president") or profile_data.get("representative_name", "entrepreneur")
        form = profile_data.get("legal_form", "SAS")
        siren = profile_data.get("siren", "")
        tva = profile_data.get("regime_tva", "Réel normal (20%)")
        imp = profile_data.get("regime_imposition", "IS")
        cloture = profile_data.get("fiscal_year_end", "31/12")
        role = profile_data.get("president_role") or profile_data.get("representative_role", "Dirigeant")

        welcome_msg = (
            f"Bonjour **{pres}**.\n\n"
            f"Votre espace pour **{comp}** est prêt et entièrement configuré.\n\n"
            f"**Fiche légale enregistrée :**\n"
            f"- **Forme juridique :** {form} {f'(SIREN {siren})' if siren else ''}\n"
            f"- **Régime fiscal :** {tva} • Imposition {imp} • Clôture au {cloture}\n"
            f"- **Représentant légal :** {pres} ({role})\n\n"
            f"Je dispose de toutes vos données légales pour votre facturation conforme 2026, votre suivi des échéances et vos formalités administratives.\n\n"
            f"Que souhaitez-vous traiter ?"
        )
        save_user_message(user_id, "assistant", welcome_msg, entity_id=target_ent_id)

    return {"success": True, "id": target_ent_id}


seed_default_testers()
