"""
Module des sources publiques d'ÉCHAP / Paperasse.
Fournit un accès ultra-rapide aux référentiels publics français :
1. Plan Comptable Général 2026 (embarqué)
2. Barème kilométrique 2026 (embarqué)
3. Nomenclature liasse fiscale (embarqué)
4. Annuaire des Entreprises / Base Sirene (API officielle + cache local SQLite)
5. DVF / Valeurs foncières (API Cerema/Etalab + cache)
"""

import os
import json
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from functools import lru_cache
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE_DB_PATH = os.path.join(DATA_DIR, "cache_sources.sqlite")


def get_cache_db() -> sqlite3.Connection:
    """Initialise et retourne la connexion SQLite de cache local."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(CACHE_DB_PATH)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sirene_cache (
                query_key TEXT PRIMARY KEY,
                siren TEXT,
                nom_complet TEXT,
                data_json TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dvf_cache (
                code_insee TEXT PRIMARY KEY,
                data_json TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    return conn


# --- 1. RECHERCHE D'ENTREPRISES (SIRENE / ANNUAIRE OFFICIEL) ---

def search_companies(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Recherche une entreprise par nom ou SIREN/SIRET.
    Vérifie d'abord le cache local SQLite sur le serveur (0ms).
    Si absent, interroge l'API officielle recherche-entreprises.api.gouv.fr et met en cache.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    # Vérification cache local
    cache_key = cleaned_query.lower().replace(" ", "")
    conn = None
    try:
        conn = get_cache_db()
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM sirene_cache WHERE query_key = ?", (cache_key,))
        row = cursor.fetchone()
        if row:
            return json.loads(row["data_json"])
    except Exception as e:
        print(f"[CACHE ERROR] {e}")
    finally:
        if conn:
            conn.close()

    # Appel API publique officielle
    encoded = urllib.parse.quote(cleaned_query)
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={encoded}&per_page={limit}"
    headers = {"User-Agent": "ECHAP-MTP/1.0 (contact@echap.local)"}
    req = urllib.request.Request(url, headers=headers)

    results = []
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            payload = json.loads(response.read().decode("utf-8"))
            raw_results = payload.get("results", [])
            for item in raw_results:
                siege = item.get("siege", {})
                results.append({
                    "siren": item.get("siren"),
                    "siret": siege.get("siret"),
                    "nom_complet": item.get("nom_complet"),
                    "nature_juridique": item.get("nature_juridique"),
                    "date_creation": item.get("date_creation"),
                    "activite_principale": item.get("activite_principale"),
                    "libelle_activite": siege.get("libelle_activite_principale"),
                    "adresse": siege.get("adresse"),
                    "code_postal": siege.get("code_postal"),
                    "ville": siege.get("libelle_commune"),
                    "etat_administratif": item.get("etat_administratif"),
                    "dirigeants": item.get("dirigeants", []),
                })
    except Exception as err:
        print(f"[API ERROR] Impossible d'interroger recherche-entreprises: {err}")
        # En cas d'absence de réseau, tenter une recherche partielle dans le cache local existant
        fb_conn = None
        try:
            fb_conn = get_cache_db()
            cursor = fb_conn.cursor()
            cursor.execute(
                "SELECT data_json FROM sirene_cache WHERE nom_complet LIKE ? LIMIT ?",
                (f"%{cleaned_query}%", limit)
            )
            rows = cursor.fetchall()
            for r in rows:
                cached_list = json.loads(r["data_json"])
                results.extend(cached_list)
        except Exception:
            pass
        finally:
            if fb_conn:
                fb_conn.close()

    # Sauvegarde dans le cache local
    if results:
        w_conn = None
        try:
            w_conn = get_cache_db()
            with w_conn:
                w_conn.execute(
                    "INSERT OR REPLACE INTO sirene_cache (query_key, siren, nom_complet, data_json) VALUES (?, ?, ?, ?)",
                    (
                        cache_key,
                        results[0].get("siren", ""),
                        results[0].get("nom_complet", ""),
                        json.dumps(results, ensure_ascii=False)
                    )
                )
                # Stocker aussi par SIREN direct pour accès instantané
                if results[0].get("siren"):
                    w_conn.execute(
                        "INSERT OR REPLACE INTO sirene_cache (query_key, siren, nom_complet, data_json) VALUES (?, ?, ?, ?)",
                        (
                            results[0]["siren"],
                            results[0].get("siren", ""),
                            results[0].get("nom_complet", ""),
                            json.dumps(results[:1], ensure_ascii=False)
                        )
                    )
        except Exception as e:
            print(f"[CACHE WRITE ERROR] {e}")
        finally:
            if w_conn:
                w_conn.close()

    return results


def seed_demo_companies():
    """Pré-charge des entreprises fictives types dans le cache local pour les tests hors-ligne."""
    demo_companies = [
        {
            "query_key": "acme",
            "results": [{
                "siren": "900123456",
                "siret": "90012345600018",
                "nom_complet": "ACME CONSEIL SAS",
                "nature_juridique": "Société par actions simplifiée",
                "date_creation": "2021-01-15",
                "activite_principale": "70.22Z",
                "libelle_activite": "Conseil pour les affaires et autres conseils de gestion",
                "adresse": "12 RUE DE LA PAIX",
                "code_postal": "75002",
                "ville": "PARIS",
                "etat_administratif": "A",
                "dirigeants": [{"nom": "DUPONT", "prenoms": "Marc", "qualite": "Président"}]
            }]
        },
        {
            "query_key": "scipierre",
            "results": [{
                "siren": "850987654",
                "siret": "85098765400012",
                "nom_complet": "SCI PIERRE & PATRIMOINE",
                "nature_juridique": "Société civile immobilière",
                "date_creation": "2019-06-20",
                "activite_principale": "68.20B",
                "libelle_activite": "Location de terrains et d'autres biens immobiliers",
                "adresse": "45 AVENUE VICTOR HUGO",
                "code_postal": "69002",
                "ville": "LYON",
                "etat_administratif": "A",
                "dirigeants": [{"nom": "MARTIN", "prenoms": "Claire", "qualite": "Gérant"}]
            }]
        },
        {
            "query_key": "martinconsulting",
            "results": [{
                "siren": "890555444",
                "siret": "89055544400015",
                "nom_complet": "MARTIN NICOLAS (EI)",
                "nature_juridique": "Entrepreneur individuel (BNC / Micro)",
                "date_creation": "2023-03-01",
                "activite_principale": "62.02A",
                "libelle_activite": "Conseil en systèmes et logiciels informatiques",
                "adresse": "8 ALLEE DES CERISIERS",
                "code_postal": "33000",
                "ville": "BORDEAUX",
                "etat_administratif": "A",
                "dirigeants": [{"nom": "MARTIN", "prenoms": "Nicolas", "qualite": "Exploitant"}]
            }]
        },
        {
            "query_key": "vitalis",
            "results": [{
                "siren": "450655147",
                "siret": "45065514700012",
                "nom_complet": "REGIE DES TRANSPORTS POITEVINS (RTP - Réseau Vitalis Poitiers)",
                "nature_juridique": "Régie d'une collectivité locale à caractère industriel ou commercial",
                "date_creation": "2003-06-20",
                "activite_principale": "49.31Z",
                "libelle_activite": "Transports urbains et suburbains de voyageurs",
                "adresse": "9 AVENUE DE NORTHAMPTON",
                "code_postal": "86000",
                "ville": "POITIERS",
                "etat_administratif": "A",
                "dirigeants": []
            }]
        },
        {
            "query_key": "vitalispoitiers",
            "results": [{
                "siren": "450655147",
                "siret": "45065514700012",
                "nom_complet": "REGIE DES TRANSPORTS POITEVINS (RTP - Réseau Vitalis Poitiers)",
                "nature_juridique": "Régie d'une collectivité locale à caractère industriel ou commercial",
                "date_creation": "2003-06-20",
                "activite_principale": "49.31Z",
                "libelle_activite": "Transports urbains et suburbains de voyageurs",
                "adresse": "9 AVENUE DE NORTHAMPTON",
                "code_postal": "86000",
                "ville": "POITIERS",
                "etat_administratif": "A",
                "dirigeants": []
            }]
        },
        {
            "query_key": "rtp",
            "results": [
                {
                    "siren": "450655147",
                    "siret": "45065514700012",
                    "nom_complet": "REGIE DES TRANSPORTS POITEVINS (RTP - Vitalis)",
                    "nature_juridique": "Régie d'une collectivité locale",
                    "date_creation": "2003-06-20",
                    "activite_principale": "49.31Z",
                    "libelle_activite": "Transports urbains et suburbains de voyageurs",
                    "adresse": "9 AVENUE DE NORTHAMPTON",
                    "code_postal": "86000",
                    "ville": "POITIERS",
                    "etat_administratif": "A",
                    "dirigeants": []
                },
                {
                    "siren": "327531372",
                    "siret": "32753137200016",
                    "nom_complet": "R.T.P.",
                    "nature_juridique": "SARL",
                    "date_creation": "1983-05-18",
                    "activite_principale": "43.34Z",
                    "libelle_activite": "Travaux de peinture et vitrerie",
                    "adresse": "18 RUE DE LARNAY",
                    "code_postal": "86000",
                    "ville": "POITIERS",
                    "etat_administratif": "A",
                    "dirigeants": []
                }
            ]
        }
    ]

    conn = None
    try:
        conn = get_cache_db()
        with conn:
            for item in demo_companies:
                conn.execute(
                    "INSERT OR IGNORE INTO sirene_cache (query_key, siren, nom_complet, data_json) VALUES (?, ?, ?, ?)",
                    (
                        item["query_key"],
                        item["results"][0]["siren"],
                        item["results"][0]["nom_complet"],
                        json.dumps(item["results"], ensure_ascii=False)
                    )
                )
                conn.execute(
                    "INSERT OR IGNORE INTO sirene_cache (query_key, siren, nom_complet, data_json) VALUES (?, ?, ?, ?)",
                    (
                        item["results"][0]["siren"],
                        item["results"][0]["siren"],
                        item["results"][0]["nom_complet"],
                        json.dumps(item["results"], ensure_ascii=False)
                    )
                )
    except Exception as err:
        print(f"[SEED ERROR] {err}")
    finally:
        if conn:
            conn.close()


# --- 2. PLAN COMPTABLE GÉNÉRAL 2026 (PCG EMBARQUÉ) ---

@lru_cache(maxsize=1)
def load_pcg_data() -> Dict[str, Any]:
    """Charge le PCG 2026 officiel en mémoire."""
    pcg_file = os.path.join(DATA_DIR, "pcg_2026.json")
    if os.path.exists(pcg_file):
        with open(pcg_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "2026", "flat": []}


def search_pcg(query: str = "", classe: Optional[int] = None, limit: int = 30) -> List[Dict[str, Any]]:
    """
    Recherche instantanée dans les comptes du PCG 2026.
    Filtre par numéro (ex: '411', '512') ou par libellé (ex: 'client', 'tva', 'banque').
    """
    data = load_pcg_data()
    flat_accounts = data.get("flat", [])

    query_clean = query.strip().lower()

    matches = []
    for acc in flat_accounts:
        num_str = str(acc.get("number", ""))
        label_clean = acc.get("label", "").lower()

        # Filtre classe (1er chiffre)
        if classe is not None and not num_str.startswith(str(classe)):
            continue

        if not query_clean:
            matches.append(acc)
        elif query_clean in num_str or query_clean in label_clean:
            matches.append(acc)

        if len(matches) >= limit:
            break

    return matches


# --- 3. BARÈME KILOMÉTRIQUE 2026 ---

@lru_cache(maxsize=1)
def load_bareme_kilometrique() -> Dict[str, Any]:
    """Charge le barème kilométrique officiel 2026."""
    bk_file = os.path.join(DATA_DIR, "bareme-kilometrique.json")
    if os.path.exists(bk_file):
        with open(bk_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def calculate_ik(cv: int, km: int, electrique: bool = False) -> Dict[str, Any]:
    """
    Calcule déterministement les indemnités kilométriques selon le barème officiel.
    Majoration électrique de 20 % appliquée si véhicule électrique.
    """
    bareme = load_bareme_kilometrique()
    autos = bareme.get("vehicules", {}).get("auto", [])

    matched_item = None
    for item in autos:
        c_min = item.get("cv_min")
        c_max = item.get("cv_max")
        if c_min is None and c_max is not None and cv <= c_max:
            matched_item = item
            break
        elif c_min is not None and c_max is None and cv >= c_min:
            matched_item = item
            break
        elif c_min is not None and c_max is not None and c_min <= cv <= c_max:
            matched_item = item
            break

    if not matched_item:
        return {"error": f"Puissance {cv} CV non reconnue"}

    # Trouver la tranche km
    tranches = matched_item.get("tranches", [])
    montant = 0.0
    details = ""
    for t in tranches:
        km_max = t.get("km_max")
        taux = float(t.get("taux_km", 0.0))
        fixe = float(t.get("fixe", 0.0))

        if km_max is not None and km <= km_max:
            montant = (km * taux) + fixe
            details = f"({km} km × {taux} €)" + (f" + {fixe} €" if fixe > 0 else "")
            break
        elif km_max is None:
            montant = (km * taux) + fixe
            details = f"({km} km × {taux} €)" + (f" + {fixe} €" if fixe > 0 else "")
            break

    if electrique:
        majoration = montant * 0.20
        montant += majoration
        details += " + majoration 20% électrique"

    return {
        "puissance_cv": cv,
        "categorie": matched_item.get("libelle"),
        "kilometres": km,
        "electrique": electrique,
        "montant_total_euros": round(montant, 2),
        "detail_calcul": details,
        "source": "Barème officiel DGFIP 2026 (art. 6B annexe IV CGI)"
    }


# --- 4. NOMENCLATURE LIASSE FISCALE ---

@lru_cache(maxsize=1)
def load_nomenclature_liasse() -> List[Dict[str, str]]:
    """Charge la nomenclature des cases de liasse fiscale."""
    csv_file = os.path.join(DATA_DIR, "nomenclature-liasse-fiscale.csv")
    results = []
    if os.path.exists(csv_file):
        with open(csv_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and ";" in line and not line.startswith("id;"):
                    parts = line.split(";", 1)
                    results.append({"code": parts[0].strip(), "libelle": parts[1].strip()})
    return results


def search_liasse_cases(query: str = "", limit: int = 25) -> List[Dict[str, str]]:
    """Recherche des cases de liasse fiscale par code (ex: 'FL', 'FP') ou mot clé."""
    data = load_nomenclature_liasse()
    q = query.strip().lower()
    if not q:
        return data[:limit]
    matches = [
        item for item in data
        if q in item["code"].lower() or q in item["libelle"].lower()
    ]
    return matches[:limit]


# Initialisation au chargement
seed_demo_companies()
