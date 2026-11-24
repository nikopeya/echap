"""
Moteur d'orchestration pour l'assistant ÉCHAP.
Routage transparent des compétences et inférence rapide à faible coût via OpenRouter.
"""

import os
import json
import httpx
from typing import Dict, Any, List, Generator, Optional

BASE_DIR = os.path.dirname(__file__)

# Modèle par défaut : ultra-rapide, économique et réactif
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "google/gemini-2.5-flash")

SKILL_KEYWORDS = {
    "comptable": ["facture", "tva", "compte", "fec", "pcg", "bilan", "clôture", "amortissement", "devis", "écriture", "fournisseur", "client", "liasse", "2033", "2065"],
    "fiscaliste": ["impôt", "revenu", "ir", "2042", "quotient", "décote", "tranche", "tmi", "ifi", "micro-foncier", "foncier", "flat tax", "pfu"],
    "notaire": ["sci", "statut", "statuts", "immobilier", "compromis", "vente", "notaire", "donation", "succession", "frais de notaire", "cadastre", "dvf"],
    "controleur-fiscal": ["contrôle", "dgfip", "rejet", "redressement", "vérification", "sanction", "irrégularité", "examen"],
    "commissaire-aux-comptes": ["audit", "nep", "commissaire", "cac", "continuité", "alerte", "revue analytique"],
    "syndic": ["copropriété", "syndic", "assemblée générale", "ag", "tantième", "charge", "appel de fonds", "conseil syndical"]
}


def detect_domain(text: str) -> str:
    """Détecte automatiquement le domaine de la demande de l'utilisateur."""
    text_lower = text.lower()
    scores = {domain: 0 for domain in SKILL_KEYWORDS}
    for domain, kws in SKILL_KEYWORDS.items():
        for kw in kws:
            if kw in text_lower:
                scores[domain] += 1
    best_domain = max(scores, key=scores.get)
    if scores[best_domain] > 0:
        return best_domain
    return "comptable"  # Domaine général par défaut


def load_domain_prompt(domain: str) -> str:
    """Charge les instructions spécialisées du domaine."""
    skill_file = os.path.join(BASE_DIR, domain, "SKILL.md")
    if os.path.exists(skill_file):
        with open(skill_file, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    return ""


def clean_domain_instructions(raw_text: str) -> str:
    """Retire toutes les références aux fichiers techniques internes, chemins de repo, traits pseudo-ascii et emojis."""
    cleaned_lines = []
    emoji_chars = ["🔴", "🟡", "🟢", "🟠", "⏰", "📋", "⚠️", "🚨", "🚀", "👋", "🛡️", "✅", "❌"]
    for line in raw_text.splitlines():
        # Éliminer les séparateurs lourds pseudo-graphiques
        stripped = line.strip()
        if stripped and all(c in "━═─- " for c in stripped) and len(stripped) > 3:
            continue
        # Éliminer toute consigne demandant de vérifier ou éditer un fichier technique interne
        if any(bad in line.lower() for bad in [
            "company.json", "setup-facturation", "references/", "copros/", "verifier si company.json existe",
            ".md", "scripts/", "data/"
        ]):
            continue
        # Nettoyer les emojis résiduels
        clean_line = line
        for em in emoji_chars:
            clean_line = clean_line.replace(em, "")
        cleaned_lines.append(clean_line)
    return "\n".join(cleaned_lines)


def build_unified_system_prompt(company_name: str, user_query: str = "", company_profile: Optional[Dict[str, Any]] = None) -> str:
    """
    Construit un prompt unifié pour ÉCHAP.
    L'agent adapte automatiquement son expertise au besoin sans que l'utilisateur n'ait à choisir.
    """
    active_domain = detect_domain(user_query) if user_query else "comptable"
    raw_instructions = load_domain_prompt(active_domain)
    domain_instructions = clean_domain_instructions(raw_instructions)

    profile_section = ""
    if company_profile:
        siren = company_profile.get("siren") or "Non renseigné"
        siret = company_profile.get("siret") or "Non renseigné"
        addr = f"{company_profile.get('address', '')} {company_profile.get('postal_code', '')} {company_profile.get('city', '')}".strip() or "Non renseignée"
        form = company_profile.get("legal_form") or "SAS"
        reg_tva = company_profile.get("regime_tva") or "Réel normal (20%)"
        reg_imp = company_profile.get("regime_imposition") or "IS"
        president = company_profile.get("president") or "Non renseigné"
        president_role = company_profile.get("president_role") or "Dirigeant"
        iban = company_profile.get("iban") or "Non renseigné"
        bic = company_profile.get("bic") or ""
        ape = company_profile.get("activity_code") or "Non renseigné"
        act_label = company_profile.get("activity_label") or ""
        fiscal_year = company_profile.get("fiscal_year_end") or "31/12"

        # Règles fiscales automatiques dérivées
        tva_directive = ""
        if "261" in reg_tva:
            tva_directive = (
                "- ATTENTION TVA (EXONÉRATION - ART. 261 D CGI) : L'activité de location nue est exonérée de TVA. "
                "Taux de TVA = 0%. Tu DOIS OBLIGATOIREMENT inscrire la mention légale : 'TVA non applicable, article 261 D du Code Général des Impôts' sur chaque facture ou quittance."
            )
        elif "Franchise" in reg_tva or "293" in reg_tva:
            tva_directive = (
                "- ATTENTION TVA (FRANCHISE EN BASE - ART. 293 B CGI) : L'entreprise est exonérée de TVA. "
                "Taux de TVA = 0%. Tu DOIS OBLIGATOIREMENT inscrire la mention légale : 'TVA non applicable, article 293 B du Code Général des Impôts' sur chaque facture ou devis."
            )
        else:
            tva_directive = (
                f"- RÉGIME TVA ASSUJETTI ({reg_tva}) : Tu appliques les taux de TVA légaux (20% par défaut) "
                "en détaillant le montant HT, le taux et montant de TVA, et le Total TTC."
            )

        profile_section = f"""
FICHE OFFICIELLE ENREGISTRÉE DE L'ENTREPRISE :
- Raison sociale : {company_name}
- Forme juridique : {form}
- SIREN : {siren}
- SIRET : {siret}
- Siège social : {addr}
- Activité / Code APE : {ape}{f' ({act_label})' if act_label else ''}
- Régime TVA : {reg_tva}
- Régime fiscal d'imposition : {reg_imp}
- Clôture d'exercice : {fiscal_year}
- Représentant légal : {president} ({president_role})
- Coordonnées bancaires : IBAN {iban}{f' / BIC {bic}' if bic else ''}

DIRECTIVES LÉGALES DIRECTEMENT APPLICABLES :
{tva_directive}
- MANDATAIRE OFFICIEL : Pour tout contrat, projet de statuts ou décision d'associés, l'entreprise est légalement représentée par {president}, agissant en qualité de {president_role}.
- COORDONNÉES BANCAIRES : Pour toute facture émise, indique automatiquement l'IBAN {iban} pour le règlement.
Tu utilises TOUJOURS ces données officielles pour répondre et générer les factures, courriers ou déclarations.
"""

    system_prompt = f"""Tu es ÉCHAP, l'assistant administratif et financier personnel des entrepreneurs et professionnels en France.
Tu travailles actuellement au service exclusif de l'entreprise : {company_name}.
{profile_section}
RÈGLES D'INTERACTION ET DE STYLE (NON NÉGOCIABLES) :
1. EXPÉRIENCE GRAND PUBLIC : L'utilisateur est un entrepreneur qui utilise une application web. Il n'est PAS un développeur.
2. ZÉRO EMOJI : N'utilise AUCUN emoji, pictogramme ou émoticône dans tes réponses (proscription totale des puces colorées, horloges, fusées, signaux d'alerte, etc.). Adopte un style sobre, professionnel, calme et précis conforme à la charte ÉCHAP. Pour indiquer une urgence ou un statut, utilise uniquement des mentions textuelles sobres entre crochets : [Urgent], [À prévoir], [Important], [Conforme], [Non configuré].
3. AUCUN SÉPARATEUR PSEUDO-ASCII : N'utilise JAMAIS de barres ou traits de séparation continus ou doubles (pas de lignes de caractères de box-drawing ou équivalents). Utilise uniquement les titres Markdown standards ('###') et les listes à tirets simples.
4. INTERDICTION STRICTE DE CITER DES FICHIERS INTERNES : Il est FORMELLEMENT INTERDIT de mentionner des fichiers techniques (fichiers json, yaml), des fichiers de configuration, ou des chemins internes du dépôt (dossiers de référence, fichiers markdown internes, scripts). L'utilisateur n'a AUCUN fichier technique à consulter ou modifier. Si une information ou un paramètre manque (ex: choix d'une plateforme de facturation électronique), demande-le ou propose de l'enregistrer directement avec lui dans la discussion.
5. SALUTATIONS ET OUVERTURE : Lors d'une simple salutation (ex: "bonjour", "salut"), réponds sobrement et poliment en demandant comment tu peux aider, SANS déballer de diagnostic complexe, de checklist ou de pavé non sollicité.
6. ACTION DIRECTE : Quand l'utilisateur te demande de préparer une facture, un devis, des statuts, une déclaration ou un courrier, GÉNÈRE DIRECTEMENT le document complet et mis en page dans ta réponse en utilisant les données de l'entreprise.
7. GESTION DES INFORMATIONS : Si une information manque (ex: IBAN ou adresse d'un client externe) :
   - Renseigne par défaut les mentions obligatoires légales françaises standards (délai 30 jours fin de mois, pénalités à 3 fois le taux d'intérêt légal, indemnité forfaitaire de 40 € pour frais de recouvrement).
   - Pour les éléments spécifiques manquants, insère un placeholder clair comme `[Votre IBAN]` et demande-le simplement en une phrase dans ta réponse.
8. CONFORMITÉ & CALCULS : Détaille systématiquement le calcul arithmétique pas à pas (Base HT, taux de TVA, montant TVA, Total TTC) et appuie-toi sur les textes en vigueur (Code de commerce, CGI, PCG 2026).
9. OUTILS AUTOMATIQUES & QUESTIONS :
   - Pour trouver le SIRET, l'adresse ou la dénomination d'un client, fournisseur ou tiers : appelle SYSTÉMATIQUEMENT le tool 'rechercher_entreprise'. Tu as accès direct en temps réel à l'Annuaire officiel des Entreprises (Sirene) ! Ne prétends JAMAIS que tu n'as pas accès à l'annuaire ou à des bases externes.
   - Quand tu as besoin d'une clarification ou de faire choisir l'utilisateur entre plusieurs options (par exemple entre 2 entreprises trouvées, ou pour choisir une option fiscale) : appelle TOUJOURS le tool 'poser_question_choix' pour lui afficher un mini-formulaire interactif élégant avec boutons, au lieu de noyer la question dans un paragraphe de texte.
   - Dès que tu prépares ou finalises une facture demandée par l'utilisateur : appelle SYSTÉMATIQUEMENT le tool 'enregistrer_facture' avec les informations du client et de la prestation. Cela génère formellement le document de facture prêt à télécharger et actualise le tableau de bord de l'entreprise.

CONNAISSANCES MÉTIER SPÉCIFIQUES :
{domain_instructions}
"""
    return system_prompt


from packages.paperasse.sources_publiques import search_companies, search_pcg, calculate_ik
from packages.paperasse.calculateurs import (
    calculer_is,
    calculer_amortissement,
    calculer_acomptes_tva,
    calculer_impot_revenu,
    analyser_fec_content
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "rechercher_entreprise",
            "description": "Recherche une entreprise, client ou fournisseur dans l'Annuaire officiel des Entreprises (Sirene) pour obtenir son SIRET, SIREN, raison sociale exacte et adresse officielle.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Nom ou marque de l'entreprise (ex: Vitalis, RTP, Doctolib) ou numéro SIREN/SIRET"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consulter_pcg",
            "description": "Recherche un compte dans le Plan Comptable Général 2026 officiel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Numéro de compte (ex: 411, 706) ou libellé"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer_indemnites_kilometriques",
            "description": "Calcule déterministement les indemnités kilométriques selon le barème officiel 2026.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cv": {"type": "integer", "description": "Puissance fiscale en CV"},
                    "km": {"type": "integer", "description": "Kilomètres parcourus"},
                    "electrique": {"type": "boolean", "description": "Véhicule électrique"}
                },
                "required": ["cv", "km"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculateur_financier",
            "description": "Exécute les calculs financiers et fiscaux déterministes certifiés selon la réglementation française : impôt sur les sociétés (IS 15%/25% et acomptes), amortissement linéaire PCG 2026 (prorata temporis), acomptes de TVA du réel simplifié (55%/40%), ou impôt sur le revenu (IR 2026 barème officiel).",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["impot_societes", "amortissement", "acomptes_tva", "impot_revenu"],
                        "description": "Type d'opération de calcul"
                    },
                    "resultat_fiscal": {"type": "number", "description": "Bénéfice fiscal imposable (pour l'IS)"},
                    "valeur_brute_ht": {"type": "number", "description": "Montant HT pour amortissement"},
                    "duree_annees": {"type": "integer", "description": "Durée d'amortissement en années (ex: 3, 5)"},
                    "mois_mise_en_service": {"type": "integer", "description": "Mois de mise en service (1 à 12, pour prorata)"},
                    "tva_n_moins_1": {"type": "number", "description": "TVA due N-1 pour les acomptes semestriels"},
                    "revenu_net_imposable": {"type": "number", "description": "Revenu net imposable annuel pour l'IR"},
                    "nb_parts": {"type": "number", "description": "Nombre de parts de quotient familial"}
                },
                "required": ["operation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyser_fec",
            "description": "Analyse un Fichier des Écritures Comptables (FEC) pour contrôler sa conformité à l'art. A.47 A-1 du LPF (18 colonnes obligatoires, équilibre débits/crédits, détection d'irrégularités ou dépenses personnelles).",
            "parameters": {
                "type": "object",
                "properties": {
                    "contenu_fec": {"type": "string", "description": "Texte ou lignes du FEC à contrôler"}
                },
                "required": ["contenu_fec"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "poser_question_choix",
            "description": "Affiche un mini-formulaire interactif avec des choix clairs quand tu as besoin d'une confirmation ou d'un choix de l'utilisateur au lieu de poser la question dans le texte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "La question posée"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Les options proposées (ex: nom des deux entreprises trouvées)"
                    },
                    "allow_custom": {"type": "boolean", "description": "Autoriser une réponse libre"}
                },
                "required": ["question", "options"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enregistrer_facture",
            "description": "Génère formellement la facture dans les documents de l'entreprise et actualise le tableau de bord financier (créances clients et TVA due). Appelle cet outil dès que tu établis ou finalises une facture demandée par l'utilisateur.",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_nom": {"type": "string", "description": "Raison sociale du client"},
                    "client_siret": {"type": "string", "description": "SIRET du client"},
                    "client_adresse": {"type": "string", "description": "Adresse du client"},
                    "description_prestation": {"type": "string", "description": "Intitulé précis de la prestation"},
                    "montant_ht": {"type": "number", "description": "Montant Hors Taxes en euros"},
                    "taux_tva": {"type": "number", "description": "Taux de TVA (ex: 0.20 pour 20%)"},
                    "delai_paiement": {"type": "string", "description": "Échéance ou délai de paiement (ex: 30 jours fin de mois)"}
                },
                "required": ["client_nom", "description_prestation", "montant_ht"]
            }
        }
    }
]


def execute_tool(name: str, args: Dict[str, Any], user_id: Optional[int] = None) -> str:
    """Exécute un outil appelé par le modèle et retourne le résultat en JSON."""
    if name == "rechercher_entreprise":
        query = args.get("query", "")
        results = search_companies(query, limit=4)
        if not results:
            words = query.strip().split()
            if len(words) > 1:
                results = search_companies(words[0], limit=4)
        return json.dumps(results, ensure_ascii=False)
    elif name == "consulter_pcg":
        query = args.get("query", "")
        res = search_pcg(query, limit=10)
        return json.dumps(res, ensure_ascii=False)
    elif name == "calculer_indemnites_kilometriques":
        cv = args.get("cv", 5)
        km = args.get("km", 1000)
        elec = args.get("electrique", False)
        ik = calculate_ik(cv, km, elec)
        return json.dumps(ik, ensure_ascii=False)
    elif name == "calculateur_financier":
        op = args.get("operation")
        if op == "impot_societes":
            res_calc = calculer_is(args.get("resultat_fiscal", 0.0))
        elif op == "amortissement":
            res_calc = calculer_amortissement(
                args.get("valeur_brute_ht", 0.0),
                args.get("duree_annees", 3),
                args.get("mois_mise_en_service", 1)
            )
        elif op == "acomptes_tva":
            res_calc = calculer_acomptes_tva(args.get("tva_n_moins_1", 0.0))
        elif op == "impot_revenu":
            res_calc = calculer_impot_revenu(
                args.get("revenu_net_imposable", 0.0),
                args.get("nb_parts", 1.0)
            )
        else:
            res_calc = {"error": f"Opération {op} inconnue"}
        return json.dumps(res_calc, ensure_ascii=False)
    elif name == "analyser_fec":
        res_fec = analyser_fec_content(args.get("contenu_fec", ""))
        return json.dumps(res_fec, ensure_ascii=False)
    elif name == "enregistrer_facture":
        if user_id:
            from packages.paperasse.auth_db import create_and_record_invoice
            res_fac = create_and_record_invoice(user_id, args)
            return json.dumps(res_fac, ensure_ascii=False)
        return json.dumps({"status": "error", "message": "user_id manquant"})
    return json.dumps({"status": "outil_inconnu"})


def run_agent_cycle(
    messages: List[Dict[str, Any]],
    api_key: str,
    model: str = DEFAULT_MODEL,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Exécute le cycle agentique avec support complet du Tool Calling et des Questions Interactives.
    Retourne {'content': str, 'question_data': Optional[dict]}.
    """
    if not api_key:
        return {
            "content": "La clé d'accès OpenRouter n'est pas configurée. Veuillez renseigner OPENROUTER_API_KEY.",
            "question_data": None
        }

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://echap.app",
        "X-Title": "ECHAP",
        "Content-Type": "application/json"
    }

    current_messages = list(messages)
    question_data = None
    max_tool_iterations = 4

    for _ in range(max_tool_iterations):
        payload = {
            "model": model,
            "messages": current_messages,
            "tools": TOOLS,
            "stream": False,
            "temperature": 0.2
        }

        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                return {
                    "content": f"Erreur OpenRouter ({resp.status_code}) : {resp.text[:300]}",
                    "question_data": None
                }
            resp_data = resp.json()

        choice = resp_data.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls", [])
        content = message.get("content") or ""

        # Si le modèle ne demande aucun outil, la réponse est finale
        if not tool_calls:
            return {"content": content, "question_data": question_data}

        # Ajouter le message de l'assistant portant les tool_calls à l'historique
        current_messages.append(message)

        # Exécution des tool calls demandés
        has_interactive_question = False
        for tc in tool_calls:
            fn_name = tc.get("function", {}).get("name")
            raw_args = tc.get("function", {}).get("arguments", "{}")
            try:
                fn_args = json.loads(raw_args)
            except Exception:
                fn_args = {}

            if fn_name == "poser_question_choix":
                question_data = {
                    "question": fn_args.get("question", ""),
                    "options": fn_args.get("options", []),
                    "allow_custom": fn_args.get("allow_custom", True)
                }
                has_interactive_question = True
                # Réponse immédiate pour valider le tool call
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "name": fn_name,
                    "content": json.dumps({"status": "question_affichee"})
                })
            else:
                # Outil de données (Sirene, PCG, IK, Facture)
                tool_output = execute_tool(fn_name, fn_args, user_id=user_id)
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "name": fn_name,
                    "content": tool_output
                })

        # Si une question interactive a été posée, le modèle termine son tour
        if has_interactive_question:
            # Appel final pour obtenir le texte introductif s'il y en a
            final_payload = {
                "model": model,
                "messages": current_messages,
                "stream": False,
                "temperature": 0.2
            }
            with httpx.Client(timeout=45.0) as client:
                f_resp = client.post(url, headers=headers, json=final_payload)
                if f_resp.status_code == 200:
                    f_content = f_resp.json().get("choices", [{}])[0].get("message", {}).get("content") or content
                    return {"content": f_content, "question_data": question_data}
            return {"content": content, "question_data": question_data}

    return {"content": content, "question_data": question_data}


def simulate_offline_response(user_query: str) -> str:
    """Réponse d'attente soignée lorsque la clé API n'est pas encore activée."""
    domain = detect_domain(user_query)
    domain_labels = {
        "comptable": "comptable & facturation",
        "fiscaliste": "fiscalité",
        "notaire": "juridique & immobilier",
        "controleur-fiscal": "conformité réglementaire",
        "commissaire-aux-comptes": "audit",
        "syndic": "gestion"
    }
    label = domain_labels.get(domain, "administratif")

    return f"""J'ai bien pris en compte votre demande concernant le volet **{label}** :

> « {user_query} »

**Points clés analysés :**
* **Référentiel applicable** : Règlementation française 2026 et Plan Comptable Général.
* **Traitement** : Qualification de l'opération, vérification des taux et calcul de l'impact financier.
* **Prochaine étape** : Consultez le tableau de bord financier ou les sources publiques pour vérifier les données associées.

*(Configurez la clé OPENROUTER_API_KEY côté serveur pour activer les réponses génératives en direct).*
"""
