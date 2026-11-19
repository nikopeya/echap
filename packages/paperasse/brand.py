"""
Module de gestion dynamique de l'identité de marque (Brand & White-Label).

Ce module relie dynamiquement le code du MTP, du MVP et des extensions futures
à la configuration canonique définie dans `assets/brand/brand.json`.
Toute modification dans le dossier de marque (couleurs, nom, baseline, logos SVG)
est répercutée automatiquement sans nécessiter de modification du code métier.
Supporte le fonctionnement en marque blanche via variable d'environnement ou substitution.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_BRAND_PATH = _PROJECT_ROOT / "assets" / "brand" / "brand.json"

_brand_cache: Optional[Dict[str, Any]] = None
_brand_cache_mtime: float = 0.0
_white_label_override: Optional[Dict[str, Any]] = None


def get_brand_config_path() -> Path:
    """Retourne le chemin vers la configuration de marque active."""
    env_path = os.environ.get("ECHAP_BRAND_CONFIG", "").strip()
    if env_path:
        custom_path = Path(env_path)
        if not custom_path.is_absolute():
            custom_path = _PROJECT_ROOT / custom_path
        if custom_path.exists():
            return custom_path
    return _DEFAULT_BRAND_PATH


def load_brand_config(force_reload: bool = False) -> Dict[str, Any]:
    """
    Charge la configuration de marque depuis le fichier JSON avec rechargement automatique
    en cas de modification du fichier (hot-reloading de l'identité de marque).
    """
    global _brand_cache, _brand_cache_mtime, _white_label_override

    if _white_label_override is not None:
        return _white_label_override

    config_path = get_brand_config_path()
    if not config_path.exists():
        # Configuration de repli minimale par défaut
        return {
            "id": "echap",
            "name": "ECHAP",
            "tagline": "Libérez-vous.",
            "baseline": "L'assistant qui libère les entrepreneurs de la paperasse.",
            "colors": {
                "primary": "#09090B",
                "primary_surface": "#18181B",
                "secondary": "#FFFFFF",
                "accent": "#EA580C",
                "accent_hover": "#C2410C",
                "accent_light": "#FFF7ED",
                "bg_page": "#F8FAFC",
                "bg_card": "#FFFFFF",
                "border": "#E2E8F0",
                "text_main": "#09090B",
                "text_secondary": "#71717A",
            },
            "assets": {
                "logo_symbol": "assets/brand/logo-echap-symbol.svg",
                "logo_horizontal": "assets/brand/logo-echap.svg",
            },
        }

    current_mtime = config_path.stat().st_mtime
    if force_reload or _brand_cache is None or current_mtime != _brand_cache_mtime:
        with open(config_path, "r", encoding="utf-8") as f:
            _brand_cache = json.load(f)
        _brand_cache_mtime = current_mtime

    return _brand_cache


def get_brand() -> Dict[str, Any]:
    """Retourne la configuration de marque active."""
    return load_brand_config()


def set_white_label(custom_brand: Union[Dict[str, Any], str, Path, None]) -> None:
    """
    Active ou désactive une marque blanche personnalisée à l'exécution.
    Permet de basculer instantanément l'apparence de l'application.
    """
    global _white_label_override
    if custom_brand is None:
        _white_label_override = None
    elif isinstance(custom_brand, (str, Path)):
        path = Path(custom_brand)
        if not path.is_absolute():
            path = _PROJECT_ROOT / path
        with open(path, "r", encoding="utf-8") as f:
            _white_label_override = json.load(f)
    elif isinstance(custom_brand, dict):
        _white_label_override = dict(custom_brand)


def get_asset_content(asset_key: str) -> str:
    """Charge et retourne le contenu textuel d'un asset vectoriel (SVG)."""
    brand = get_brand()
    assets = brand.get("assets", {})
    relative_path = assets.get(asset_key, "")
    if not relative_path:
        return ""

    full_path = _PROJECT_ROOT / relative_path
    if not full_path.exists():
        return ""

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


import re

def get_logo_svg(variant: str = "horizontal", height: int = 40) -> str:
    """
    Retourne le logo vectoriel SVG adapté avec la hauteur demandée,
    minifié sur une seule ligne pour éviter tout artefact de code block Markdown dans Streamlit.
    Variants disponibles: 'horizontal', 'symbol', 'dark'.
    """
    key_map = {
        "horizontal": "logo_horizontal",
        "symbol": "logo_symbol",
        "dark": "logo_dark",
    }
    asset_key = key_map.get(variant, "logo_horizontal")
    raw_svg = get_asset_content(asset_key)
    if not raw_svg:
        # Fallback textuel si l'asset manque
        brand = get_brand()
        return f"<div style='font-size: 20px; font-weight: 800; color: #09090B;'>{brand.get('name', 'ECHAP')}</div>"

    # Minification sur une seule ligne : élimine tous les retours chariots et indentations
    minified_svg = re.sub(r"\s+", " ", raw_svg).strip()

    # Injection propre de style pour respecter la hauteur demandée
    if "<svg" in minified_svg:
        styled_svg = minified_svg.replace(
            "<svg ",
            f'<svg style="height: {height}px; width: auto; max-width: 100%; display: inline-block; vertical-align: middle;" ',
            1
        )
        return styled_svg
    return minified_svg


def get_brand_css() -> str:
    """
    Génère les variables CSS et classes utilitaires injectées dans l'interface,
    garantissant que toute modification de palette s'applique instantanément.
    """
    brand = get_brand()
    colors = brand.get("colors", {})
    status = brand.get("status_colors", {})
    typo = brand.get("typography", {})

    primary = colors.get("primary", "#09090B")
    primary_surface = colors.get("primary_surface", "#18181B")
    accent = colors.get("accent", "#EA580C")
    accent_hover = colors.get("accent_hover", "#C2410C")
    accent_light = colors.get("accent_light", "#FFF7ED")
    accent_border = colors.get("accent_border", "#FFEDD5")
    bg_page = colors.get("bg_page", "#F8FAFC")
    border = colors.get("border", "#E2E8F0")
    text_main = colors.get("text_main", "#09090B")
    text_secondary = colors.get("text_secondary", "#71717A")

    success_color = status.get("success", {}).get("text", "#047857")
    success_bg = status.get("success", {}).get("bg", "#ECFDF5")

    return f"""
    <style>
        :root {{
            --brand-primary: {primary};
            --brand-primary-surface: {primary_surface};
            --brand-accent: {accent};
            --brand-accent-hover: {accent_hover};
            --brand-accent-light: {accent_light};
            --brand-accent-border: {accent_border};
            --brand-bg: {bg_page};
            --brand-border: {border};
            --brand-text-main: {text_main};
            --brand-text-secondary: {text_secondary};
            --brand-font-body: {typo.get('body', 'sans-serif')};
        }}

        /* Style global lié à la marque */
        .block-container {{
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }}

        /* Cartes de métriques dynamiques */
        .metric-card {{
            background: #ffffff;
            border: 1px solid var(--brand-border);
            border-radius: 10px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        .metric-card:hover {{
            border-color: var(--brand-accent);
            box-shadow: 0 4px 12px rgba(234, 88, 12, 0.06);
        }}
        .metric-label {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--brand-text-secondary);
            font-weight: 600;
            margin-bottom: 6px;
        }}
        .metric-value {{
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--brand-primary);
            letter-spacing: -0.02em;
        }}
        .metric-sub {{
            font-size: 0.78rem;
            color: {success_color};
            margin-top: 4px;
            font-weight: 500;
        }}

        /* Badges d'accentuation */
        .badge-brand-accent {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: var(--brand-accent-light);
            border: 1px solid var(--brand-accent-border);
            color: var(--brand-accent);
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            letter-spacing: 0.02em;
        }}

        /* En-tête de marque */
        .brand-header-box {{
            text-align: center;
            padding: 10px 0 20px 0;
        }}
        .brand-tagline {{
            color: var(--brand-text-secondary);
            font-size: 14px;
            margin-top: 8px;
            letter-spacing: 0.01em;
        }}

        /* Masquer éléments parasites Streamlit */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
    </style>
    """


import textwrap

def render_brand_login_header() -> str:
    """Génère le header de marque pour l'écran de connexion."""
    brand = get_brand()
    logo_svg = get_logo_svg(variant="horizontal", height=48)
    tagline = brand.get("tagline", "Libérez-vous.")
    baseline = brand.get("baseline", "L'assistant qui libère les entrepreneurs de la paperasse.")

    return f'<div class="brand-header-box"><div>{logo_svg}</div><p class="brand-tagline"><strong>{tagline}</strong> — {baseline}</p></div>'


def render_brand_sidebar_header(company_name: str) -> str:
    """Génère le logo et le titre dans la barre latérale."""
    logo_svg = get_logo_svg(variant="horizontal", height=32)
    return f'<div style="margin-bottom: 12px;"><div>{logo_svg}</div><div style="font-size: 12px; color: #71717A; margin-top: 4px; font-weight: 600;">{company_name}</div></div>'
