"""
Gestion des espaces testeurs (tenants), pièces fictives et génération de restitutions.
Assure l'isolation stricte des fichiers entre espaces de test (DEC-025 / DEC-027).
"""

import os
import re
import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

STORAGE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "tenants")


def get_tenant_dirs(tenant_id: str) -> Dict[str, str]:
    """Retourne et crée les répertoires d'upload et d'export d'un tenant."""
    # Nettoyage de l'identifiant pour éviter tout directory traversal
    safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "_", tenant_id).strip() or "demo"
    tenant_base = os.path.join(STORAGE_ROOT, safe_id)
    uploads_dir = os.path.join(tenant_base, "uploads")
    exports_dir = os.path.join(tenant_base, "exports")
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(exports_dir, exist_ok=True)
    return {
        "base": tenant_base,
        "uploads": uploads_dir,
        "exports": exports_dir
    }


def save_fictitious_file(tenant_id: str, filename: str, content_bytes: bytes) -> str:
    """Enregistre une pièce fictive dans l'espace isolé du testeur."""
    dirs = get_tenant_dirs(tenant_id)
    safe_filename = os.path.basename(filename)
    dest_path = os.path.join(dirs["uploads"], safe_filename)
    with open(dest_path, "wb") as f:
        f.write(content_bytes)
    return dest_path


def list_tenant_files(tenant_id: str, kind: str = "uploads") -> List[Dict[str, Any]]:
    """Liste les fichiers présents dans l'espace du testeur."""
    dirs = get_tenant_dirs(tenant_id)
    target_dir = dirs.get(kind, dirs["uploads"])
    items = []
    if os.path.exists(target_dir):
        for fname in os.listdir(target_dir):
            fpath = os.path.join(target_dir, fname)
            if os.path.isfile(fpath):
                stat = os.stat(fpath)
                items.append({
                    "name": fname,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
                    "path": fpath
                })
    return items


def generate_sample_fec(tenant_id: str, company_name: str, siren: str) -> str:
    """Génère un fichier FEC fictif conforme au format DGFiP (18 colonnes séparées par tabulation)."""
    dirs = get_tenant_dirs(tenant_id)
    fec_filename = f"{siren}FEC20261231.txt"
    dest_path = os.path.join(dirs["exports"], fec_filename)

    headers = [
        "JournalCode", "JournalLib", "EcritureNum", "EcritureDate", "CompteNum", "CompteLib",
        "CompAuxNum", "CompAuxLib", "PieceRef", "PieceDate", "EcritureLib",
        "Debit", "Credit", "EcritureLet", "DateLet", "ValidDate", "Montantdevise", "Idevise"
    ]

    entries = [
        ["VE", "Journal des Ventes", "V0001", "20260115", "411100", "Clients - Ventes", "", "", "FAC-2026-001", "20260115", "Facture prestation ACME", "1200,00", "0,00", "", "", "20260115", "", ""],
        ["VE", "Journal des Ventes", "V0001", "20260115", "706000", "Prestations de services", "", "", "FAC-2026-001", "20260115", "Facture prestation ACME", "0,00", "1000,00", "", "", "20260115", "", ""],
        ["VE", "Journal des Ventes", "V0001", "20260115", "445710", "TVA collectee 20%", "", "", "FAC-2026-001", "20260115", "Facture prestation ACME", "0,00", "200,00", "", "", "20260115", "", ""],
        ["BQ", "Banque", "B0001", "20260120", "512000", "Banque compte courant", "", "", "VIR-ACME", "20260120", "Reglement client ACME", "1200,00", "0,00", "", "", "20260120", "", ""],
        ["BQ", "Banque", "B0001", "20260120", "411100", "Clients - Ventes", "", "", "VIR-ACME", "20260120", "Reglement client ACME", "0,00", "1200,00", "", "", "20260120", "", ""],
    ]

    with open(dest_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(headers)
        for row in entries:
            writer.writerow(row)

    return dest_path


def generate_sample_report(tenant_id: str, skill_id: str, title: str, content: str) -> str:
    """Génère une restitution Markdown dans les exports du testeur."""
    dirs = get_tenant_dirs(tenant_id)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"restitution_{skill_id}_{timestamp}.md"
    dest_path = os.path.join(dirs["exports"], fname)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n*Généré par ÉCHAP MTP (Skill: {skill_id}) — Cas Fictif*\n*Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}*\n\n---\n\n{content}")
    return dest_path
