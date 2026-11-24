"""
Règles pures du parcours d'onboarding ÉCHAP.

Ce module ne dépend pas de Streamlit. Il centralise les valeurs par défaut,
le mapping des formes juridiques renvoyées par l'Annuaire des entreprises et
les choix de TVA, afin que le formulaire reste cohérent entre les structures
et testable sans interface.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


TVA_FRANCHISE = "Franchise en base de TVA (art. 293 B du CGI - exonéré)"
TVA_NORMAL = "Réel normal (20%)"
TVA_SIMPLIFIE = "Réel simplifié"
TVA_EXONERATION_261D = "Exonération de TVA (art. 261 D du CGI - location nue)"

TVA_TITLE = "Quel régime de TVA s'applique à votre structure ?"

TVA_SUBTITLES = {
    "micro_enterprise": (
        "Au démarrage, la franchise en base est le régime le plus fréquent. "
        "Vous pourrez en changer à tout moment."
    ),
    "company": (
        "Une société est en principe assujettie à la TVA. La franchise en base "
        "n'est possible que si son chiffre d'affaires reste sous les seuils légaux."
    ),
    "sci": (
        "Les locations nues sont exonérées de TVA. La TVA ne concerne que les "
        "locations meublées ou les prestations facturées par la SCI."
    ),
    "liberal": (
        "La franchise en base est fréquente au démarrage, mais elle dépend de "
        "votre activité et de vos recettes. Ce choix reste modifiable."
    ),
}

STRUCTURE_DEFAULTS: Dict[str, Dict[str, str]] = {
    "micro_enterprise": {
        "legal_form": "Micro-entreprise",
        "regime_tva": TVA_FRANCHISE,
        "regime_imposition": "IR",
        "president_role": "Entrepreneur individuel",
    },
    "company": {
        "legal_form": "SAS",
        "regime_tva": TVA_NORMAL,
        "regime_imposition": "IS",
        "president_role": "Président",
    },
    "sci": {
        "legal_form": "SCI",
        "regime_tva": TVA_EXONERATION_261D,
        "regime_imposition": "IR",
        "president_role": "Gérant",
    },
    "liberal": {
        "legal_form": "Profession libérale (BNC)",
        "regime_tva": TVA_FRANCHISE,
        "regime_imposition": "IR",
        "president_role": "Titulaire libéral",
    },
}

LEGAL_FORMS_BY_TYPE: Dict[str, List[str]] = {
    "company": ["SAS", "SASU", "SARL", "EURL", "SA", "SNC", "Autre société"],
    "sci": ["SCI"],
    "liberal": ["Profession libérale (BNC)"],
    "micro_enterprise": ["Micro-entreprise"],
}

REPRESENTATIVE_ROLES = [
    "Président",
    "Directeur Général",
    "Gérant",
    "Associé gérant",
    "Entrepreneur individuel",
    "Titulaire libéral",
    "Titulaire",
]


def _has_word(text: str, word: str) -> bool:
    """Vrai si ``word`` apparaît comme mot isolé (évite « SCIentifique »)."""
    return re.search(rf"(?<![A-Z0-9]){re.escape(word)}(?![A-Z0-9])", text) is not None


def legal_forms_for(structure_type: str) -> List[str]:
    """Formes juridiques proposées pour une structure donnée."""
    return LEGAL_FORMS_BY_TYPE.get(structure_type, LEGAL_FORMS_BY_TYPE["company"])


def structure_defaults(structure_type: str) -> Dict[str, str]:
    """Valeurs fiscales par défaut cohérentes avec le type de structure."""
    return dict(STRUCTURE_DEFAULTS.get(structure_type, STRUCTURE_DEFAULTS["company"]))


def select_structure(draft: Dict[str, Any], structure_type: str, full_name: str = "") -> Dict[str, Any]:
    """
    Applique le type de structure choisi au brouillon.

    Si le type change, les informations d'identité déjà saisies sont remises à
    zéro pour éviter de conserver un nom ou une adresse appartenant à l'ancien
    type (ex. « Prénom EI » quand on bascule vers une société).
    """
    previous_type = draft.get("structure_type")
    if previous_type != structure_type:
        for key in (
            "name",
            "siren",
            "siret",
            "address",
            "postal_code",
            "city",
            "activity_code",
            "activity_label",
        ):
            draft[key] = ""

    draft["structure_type"] = structure_type
    draft.update(structure_defaults(structure_type))

    if structure_type == "micro_enterprise":
        draft["name"] = f"{full_name} EI" if full_name else "Mon Activité Indépendante"
    return draft


def _upper_company_text(company: Dict[str, Any]) -> str:
    text = " ".join(
        str(company.get(key) or "")
        for key in ("nature_juridique", "nom_complet", "denomination")
    )
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return text.upper()


def legal_form_from_company(company: Dict[str, Any]) -> str:
    """
    Déduit la forme juridique d'un résultat de l'Annuaire officiel.

    L'API renvoie parfois un code INSEE (5710, 5499…), parfois un libellé
    (« Société civile immobilière »). Le nom commercial sert aussi de secours
    pour distinguer SASU d'une SAS et EURL d'une SARL.
    """
    nature = str(company.get("nature_juridique") or "").strip()
    code = nature if nature.isdigit() else ""
    text = _upper_company_text(company)

    if "SASU" in text or code == "5720" or "ACTIONS SIMPLIFIEE UNIPERSONNELLE" in text:
        return "SASU"
    if "EURL" in text or code == "5498":
        return "EURL"
    if (
        _has_word(text, "SCI")
        or "CIVILE IMMOBILIERE" in text
        or code in {"6540", "5308"}
    ):
        return "SCI"
    if (
        _has_word(text, "SAS")
        or code == "5710"
        or "ACTIONS SIMPLIFIEE" in text
    ):
        return "SAS"
    if (
        _has_word(text, "SARL")
        or code == "5499"
        or "RESPONSABILITE LIMITEE" in text
    ):
        return "SARL"
    if (
        _has_word(text, "SNC")
        or code == "5202"
        or "NOM COLLECTIF" in text
    ):
        return "SNC"
    if code == "5505" or "SOCIETE ANONYME" in text:
        return "SA"
    if (
        code == "1000"
        or "ENTREPRISE INDIVIDUELLE" in text
        or "MICRO-ENTREPRISE" in text
        or "MICRO-ENTREPRENEUR" in text
    ):
        return "Micro-entreprise"
    if any(
        label in text
        for label in (
            "PROFESSION LIBERALE",
            "SELARL",
            "SELAS",
            "SOCIETE CIVILE DE MOYENS",
            "SCM",
            "SCP",
        )
    ):
        return "Profession libérale (BNC)"
    return ""


def structure_type_for_legal_form(legal_form: str) -> str:
    """Associe une forme juridique au type de parcours correspondant."""
    if legal_form == "Micro-entreprise":
        return "micro_enterprise"
    if legal_form == "SCI":
        return "sci"
    if legal_form == "Profession libérale (BNC)":
        return "liberal"
    return "company"


def representative_from_company(
    company: Dict[str, Any], fallback_name: str = "", default_role: str = "Dirigeant"
) -> Tuple[str, str]:
    """Extrait le représentant légal et sa qualité depuis les dirigeants Sirene."""
    for dirigeant in company.get("dirigeants", []) or []:
        if dirigeant.get("type_dirigeant") == "personne morale":
            continue
        qualite = str(dirigeant.get("qualite") or "")
        low = qualite.lower()
        if "commissaire aux comptes" in low:
            continue
        if "président" in low:
            role = "Président"
        elif "gérant" in low:
            role = "Gérant"
        elif "directeur général" in low:
            role = "Directeur Général"
        elif "exploitant" in low:
            role = "Entrepreneur individuel"
        elif "associé" in low:
            role = "Associé gérant"
        elif "titulaire" in low:
            role = "Titulaire libéral"
        else:
            continue
        name = f"{dirigeant.get('prenoms') or ''} {dirigeant.get('nom') or ''}".strip()
        if name:
            return name, role
    return fallback_name, default_role


def _clean_registry_address(address: str, postal_code: str, city: str) -> str:
    """
    Retire le code postal et la ville déjà inclus dans l'adresse de l'Annuaire.

    L'API renvoie parfois « 54 quai Charles Pasqua 92300 Levallois-Perret ».
    Le formulaire stocke l'adresse, le code postal et la ville séparément :
    sans ce nettoyage, la facture afficherait deux fois le code postal et la ville.
    """
    cleaned = str(address or "").strip()
    suffixes = [
        f"{postal_code} {city}",
        f"{city} {postal_code}",
    ]
    for suffix in suffixes:
        suffix = suffix.strip()
        if suffix and cleaned.upper().endswith(suffix.upper()):
            cleaned = cleaned[: -len(suffix)].strip(" ,;-")
            break
    return cleaned


def apply_company_to_draft(
    draft: Dict[str, Any], company: Dict[str, Any], fallback_name: str = ""
) -> Dict[str, Any]:
    """Reporte un résultat de l'Annuaire dans le brouillon d'onboarding."""
    postal_code = company.get("code_postal") or ""
    city = company.get("ville") or ""
    draft["name"] = company.get("nom_complet") or draft.get("name", "")
    draft["siren"] = company.get("siren") or ""
    draft["siret"] = company.get("siret") or ""
    draft["address"] = _clean_registry_address(company.get("adresse"), postal_code, city)
    draft["postal_code"] = postal_code
    draft["city"] = city
    draft["activity_code"] = company.get("activite_principale") or ""
    draft["activity_label"] = company.get("libelle_activite") or ""

    legal_form = legal_form_from_company(company)
    if legal_form:
        structure_type = structure_type_for_legal_form(legal_form)
        if structure_type != draft.get("structure_type"):
            draft["structure_type"] = structure_type
            draft.update(structure_defaults(structure_type))
        draft["legal_form"] = legal_form

    default_role = structure_defaults(draft.get("structure_type", "company"))["president_role"]
    president, role = representative_from_company(company, fallback_name, default_role)
    draft["president"] = president
    draft["president_role"] = role
    return draft


def company_suggestion_label(company: Dict[str, Any]) -> str:
    """Libellé lisible d'une suggestion d'autocomplétion."""
    name = company.get("nom_complet") or "Structure sans nom"
    siren = company.get("siren") or "SIREN inconnu"
    city = company.get("ville") or ""
    label = f"{name} — SIREN {siren}"
    if city:
        label += f" — {city}"
    return label


def tva_choices(structure_type: str) -> List[Dict[str, str]]:
    """
    Choix de TVA ordonnés et expliqués pour le type de structure.

    Le premier choix est le cas le plus courant pour ce type de structure et
    sert de valeur par défaut si l'utilisateur répond « Je ne sais pas ».
    """
    if structure_type == "company":
        return [
            {
                "key": "normal",
                "value": TVA_NORMAL,
                "title": "Oui, TVA à 20 % (régime réel normal)",
                "description": "Déclaration mensuelle ou trimestrielle. Vous déduisez la TVA de vos achats professionnels.",
                "badge": "Le plus courant",
            },
            {
                "key": "simplifie",
                "value": TVA_SIMPLIFIE,
                "title": "Oui, TVA avec déclaration annuelle (réel simplifié)",
                "description": "Vous versez des acomptes semestriels puis une déclaration annuelle.",
                "badge": "Moins de paperasse",
            },
            {
                "key": "franchise",
                "value": TVA_FRANCHISE,
                "title": "Non, franchise en base (sous conditions de chiffre d'affaires)",
                "description": "Possible uniquement pour une société dont le chiffre d'affaires reste sous les seuils légaux. Mention art. 293 B sur les factures.",
                "badge": "Sous conditions",
            },
        ]

    if structure_type == "sci":
        return [
            {
                "key": "exoneration_261d",
                "value": TVA_EXONERATION_261D,
                "title": "Non, mes loyers sont exonérés de TVA",
                "description": "Location nue : mention « TVA non applicable, art. 261 D du CGI ». Aucune TVA sur les loyers.",
                "badge": "Le plus courant",
            },
            {
                "key": "normal",
                "value": TVA_NORMAL,
                "title": "Oui, TVA à 20 % (location meublée ou prestations)",
                "description": "Déclaration mensuelle ou trimestrielle. Vous déduisez la TVA de vos achats.",
                "badge": "Si assujettie",
            },
            {
                "key": "simplifie",
                "value": TVA_SIMPLIFIE,
                "title": "Oui, TVA avec déclaration annuelle (réel simplifié)",
                "description": "Acomptes semestriels et déclaration annuelle de TVA.",
                "badge": "Moins de paperasse",
            },
        ]

    if structure_type == "liberal":
        return [
            {
                "key": "franchise",
                "value": TVA_FRANCHISE,
                "title": "Non, je ne facture pas de TVA",
                "description": "Franchise en base : aucune TVA à ajouter, mention art. 293 B sur vos factures.",
                "badge": "Fréquent au démarrage",
            },
            {
                "key": "normal",
                "value": TVA_NORMAL,
                "title": "Oui, TVA à 20 % (régime réel normal)",
                "description": "Déclaration mensuelle ou trimestrielle. Vous déduisez la TVA de vos achats.",
                "badge": "Si assujetti",
            },
            {
                "key": "simplifie",
                "value": TVA_SIMPLIFIE,
                "title": "Oui, TVA avec déclaration annuelle (réel simplifié)",
                "description": "Acomptes semestriels et déclaration annuelle de TVA.",
                "badge": "Moins de paperasse",
            },
        ]

    return [
        {
            "key": "franchise",
            "value": TVA_FRANCHISE,
            "title": "Non, je ne facture pas de TVA",
            "description": "Franchise en base : aucune TVA à ajouter, mention art. 293 B sur vos factures.",
            "badge": "Le plus courant",
        },
        {
            "key": "normal",
            "value": TVA_NORMAL,
            "title": "Oui, TVA à 20 % (régime réel normal)",
            "description": "Déclaration mensuelle ou trimestrielle. Vous déduisez la TVA de vos achats.",
            "badge": "Si assujetti",
        },
        {
            "key": "simplifie",
            "value": TVA_SIMPLIFIE,
            "title": "Oui, TVA avec déclaration annuelle (réel simplifié)",
            "description": "Acomptes semestriels et déclaration annuelle de TVA.",
            "badge": "Moins de paperasse",
        },
    ]


def tva_subtitle(structure_type: str) -> str:
    """Explication du régime TVA adaptée au type de structure."""
    return TVA_SUBTITLES.get(structure_type, TVA_SUBTITLES["company"])


def role_options(current_role: Optional[str] = None) -> List[str]:
    """Rôles proposés, en conservant le rôle déjà choisi s'il est atypique."""
    roles = list(REPRESENTATIVE_ROLES)
    if current_role and current_role not in roles:
        roles.append(current_role)
    return roles


def missing_identity_fields(draft: Dict[str, Any]) -> List[str]:
    """Champs nécessaires à une facture conforme encore absents."""
    missing = []
    if not str(draft.get("name") or "").strip():
        missing.append("le nom de la structure")
    if not str(draft.get("address") or "").strip():
        missing.append("l'adresse")
    if not str(draft.get("postal_code") or "").strip():
        missing.append("le code postal")
    if not str(draft.get("city") or "").strip():
        missing.append("la ville")
    return missing
