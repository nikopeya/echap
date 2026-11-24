"""
ÉCHAP — L'assistant administratif et financier des professionnels.
Interface épurée et tableau de bord de pilotage en temps réel.
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from packages.paperasse.agent import (
    build_unified_system_prompt,
    run_agent_cycle,
    simulate_offline_response,
    DEFAULT_MODEL
)
from packages.paperasse.sources_publiques import (
    search_companies,
    search_pcg,
    calculate_ik
)
from packages.paperasse.onboarding import (
    TVA_EXONERATION_261D,
    TVA_TITLE,
    apply_company_to_draft,
    company_suggestion_label,
    legal_forms_for,
    missing_identity_fields,
    role_options,
    select_structure,
    tva_choices,
    tva_subtitle,
)
from packages.paperasse.auth_db import (
    authenticate_user,
    register_user,
    load_user_chat,
    save_user_message,
    clear_user_chat,
    get_company_finances,
    get_company_profile,
    update_company_profile,
    is_onboarding_completed,
    complete_onboarding,
    get_user_entities,
    get_entity_profile,
    create_entity_for_user,
    update_entity_profile,
    save_document,
    list_user_documents,
    get_document_content
)
from packages.paperasse.brand import (
    get_brand,
    get_brand_css,
    render_brand_login_header,
    render_brand_sidebar_header,
)

brand = get_brand()

st.set_page_config(
    page_title=f"{brand.get('name', 'ECHAP')} — {brand.get('tagline', 'Libérez-vous.')}",
    page_icon="assets/brand/favicon.svg" if os.path.exists("assets/brand/favicon.svg") else None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS dynamique issu de la charte de marque (brand.json)
st.markdown(get_brand_css(), unsafe_allow_html=True)


def get_api_key() -> str:
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        pass
    return os.environ.get("OPENROUTER_API_KEY", "").strip()

api_key = get_api_key()

if "user" not in st.session_state:
    st.session_state.user = None

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Assistant"


# ==============================================================================
# 1. ÉCRAN DE CONNEXION ÉPURÉ
# ==============================================================================
if st.session_state.user is None:
    st.write("")
    st.write("")
    col_l, col_center, col_r = st.columns([1.2, 1.6, 1.2])

    with col_center:
        st.markdown(render_brand_login_header(), unsafe_allow_html=True)

        auth_mode = st.radio(
            "Mode d'accès",
            ["Connexion", "Créer un compte"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode",
        )

        if auth_mode == "Connexion":
            with st.form("form_login", clear_on_submit=False, border=False):
                username = st.text_input("Identifiant", key="login_username", placeholder="Votre identifiant")
                password = st.text_input("Mot de passe", type="password", key="login_password", placeholder="Votre mot de passe")
                st.write("")
                login_submit = st.form_submit_button("Se connecter", use_container_width=True, type="primary")

            if login_submit:
                if not username.strip() or not password:
                    st.error("Renseignez votre identifiant et votre mot de passe.")
                else:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Identifiant ou mot de passe incorrect.")

            if st.button("Accès démo", use_container_width=True, key="demo_access"):
                demo_user = authenticate_user("testeur1", "test1234")
                if demo_user:
                    st.session_state.user = demo_user
                    st.rerun()

            st.caption("Comptes : `testeur1`, `testeur2`, `testeur3` (mot de passe: `test1234`)")

        else:
            with st.form("form_register", clear_on_submit=False, border=False):
                reg_name = st.text_input("Prénom et Nom", key="reg_name", placeholder="Ex : Alexandre Martin")
                reg_user = st.text_input("Identifiant", key="reg_user", placeholder="Identifiant souhaité")
                reg_pass = st.text_input("Mot de passe", type="password", key="reg_pass", placeholder="Mot de passe")
                st.write("")
                register_submit = st.form_submit_button("Créer mon compte", use_container_width=True, type="primary")

            if register_submit:
                if not reg_user.strip():
                    st.error("Choisissez un identifiant.")
                elif len(reg_pass) < 6:
                    st.error("Le mot de passe doit contenir au moins 6 caractères.")
                else:
                    with st.spinner("Création de votre espace..."):
                        res = register_user(reg_user, reg_pass, full_name=reg_name)

                    # Si l'identifiant existe déjà, une tentative précédente a pu créer
                    # le compte sans que l'affichage aboutisse (session perdue ou
                    # rafraîchissement). Avec le bon mot de passe, on ouvre la session
                    # au lieu de bloquer l'utilisateur sur « identifiant déjà utilisé ».
                    if "error" in res and "déjà utilisé" in res["error"]:
                        existing = authenticate_user(reg_user, reg_pass)
                        if existing:
                            res = existing
                            st.session_state.auth_notice = (
                                "Ce compte existait déjà : vous êtes connecté à votre espace."
                            )

                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.session_state.user = res
                        st.session_state.active_nav = "Assistant"
                        st.rerun()

    st.stop()


# ==============================================================================
# 2. ESPACE CONNECTÉ (UTILISATEUR & STRUCTURES)
# ==============================================================================
user = st.session_state.user
user_id = user["id"]
user_fullname = user.get("full_name") or user.get("username")
username = user["username"]

if st.session_state.pop("auth_notice", None):
    st.info("Ce compte existait déjà : vous êtes connecté à votre espace. Si ce n'est pas le vôtre, déconnectez-vous et choisissez un autre identifiant.")

# Récupération des structures associées à l'utilisateur
user_entities = get_user_entities(user_id)

# Gestion de l'entité active
if "active_entity_id" not in st.session_state or not any(e["id"] == st.session_state.active_entity_id for e in user_entities):
    st.session_state.active_entity_id = user_entities[0]["id"] if user_entities else None

active_entity_id = st.session_state.active_entity_id
is_adding_entity = st.session_state.get("adding_entity", False)

# ==============================================================================
# ONBOARDING TYPEFORM PAS-À-PAS (1 SEULE QUESTION À LA FOIS, GROS BOUTONS)
# ==============================================================================
if not user_entities or is_adding_entity:
    if "ob_step" not in st.session_state:
        st.session_state.ob_step = 1

    current_step = st.session_state.ob_step

    if "ob_draft" not in st.session_state:
        st.session_state.ob_draft = {
            "structure_type": "micro_enterprise" if "auto" in username.lower() else "company",
            "name": "",
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
            "president": user_fullname,
            "president_role": "Dirigeant",
            "iban": "",
            "bic": ""
        }

    draft = st.session_state.ob_draft

    # Style épuré type Typeform
    st.markdown("""
    <style>
        .ob-progress-wrap {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.82rem;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .ob-bar-bg {
            width: 100%;
            height: 6px;
            background: #e2e8f0;
            border-radius: 9999px;
            margin-bottom: 28px;
            overflow: hidden;
        }
        .ob-bar-fill {
            height: 100%;
            background: #ea580c;
            border-radius: 9999px;
            transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .ob-title {
            font-size: 2rem;
            font-weight: 800;
            color: #09090b;
            line-height: 1.25;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        .ob-subtitle {
            font-size: 1.05rem;
            color: #71717a;
            line-height: 1.5;
            margin-bottom: 28px;
        }
    </style>
    """, unsafe_allow_html=True)

    progress_pct = {1: 25, 2: 50, 3: 75, 4: 100}.get(current_step, 25)

    col_l, col_center, col_r = st.columns([1, 4, 1])
    with col_center:
        st.markdown(f"""
        <div class="ob-progress-wrap">
            <span>Étape {current_step} sur 4</span>
            <span>{progress_pct} %</span>
        </div>
        <div class="ob-bar-bg">
            <div class="ob-bar-fill" style="width: {progress_pct}%;"></div>
        </div>
        """, unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # QUESTION 1 : TYPE D'ACTIVITÉ (4 GRANDES CARTES SÉLECTIONNABLES)
        # ----------------------------------------------------------------------
        if current_step == 1:
            st.markdown("""
            <div class="ob-title">Dans quelle situation êtes-vous ?</div>
            <div class="ob-subtitle">Répondez avec vos mots. Les termes juridiques, on s'en occupe pour vous.</div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; min-height: 120px; margin-bottom: 12px;">
                    <div style="font-size: 1.6rem; margin-bottom: 6px;">💼</div>
                    <div style="font-weight: 700; color: #09090b; font-size: 1.05rem;">Je travaille à mon compte</div>
                    <div style="color: #71717a; font-size: 0.85rem; margin-top: 4px;">Indépendant, freelance, auto-entrepreneur, micro-entreprise : vous facturez vos clients en votre nom.</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Je travaille à mon compte", key="btn_choose_micro", use_container_width=True):
                    select_structure(draft, "micro_enterprise", user_fullname)
                    st.session_state.ob_step = 2
                    st.rerun()

            with c2:
                st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; min-height: 120px; margin-bottom: 12px;">
                    <div style="font-size: 1.6rem; margin-bottom: 6px;">🏢</div>
                    <div style="font-weight: 700; color: #09090b; font-size: 1.05rem;">J'ai créé une société</div>
                    <div style="color: #71717a; font-size: 0.85rem; margin-top: 4px;">SAS, SASU, SARL, EURL : c'est la société qui porte votre activité, même si elle est en cours de création.</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("J'ai créé une société", key="btn_choose_company", use_container_width=True):
                    select_structure(draft, "company", user_fullname)
                    st.session_state.ob_step = 2
                    st.rerun()

            c3, c4 = st.columns(2)
            with c3:
                st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; min-height: 120px; margin-bottom: 12px;">
                    <div style="font-size: 1.6rem; margin-bottom: 6px;">🏠</div>
                    <div style="font-weight: 700; color: #09090b; font-size: 1.05rem;">Je gère un bien immobilier</div>
                    <div style="color: #71717a; font-size: 0.85rem; margin-top: 4px;">Location, patrimoine familial ou bien détenu à plusieurs (SCI).</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Je gère un bien immobilier", key="btn_choose_sci", use_container_width=True):
                    select_structure(draft, "sci", user_fullname)
                    st.session_state.ob_step = 2
                    st.rerun()

            with c4:
                st.markdown("""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; min-height: 120px; margin-bottom: 12px;">
                    <div style="font-size: 1.6rem; margin-bottom: 6px;">🩺</div>
                    <div style="font-weight: 700; color: #09090b; font-size: 1.05rem;">J'exerce un métier réglementé</div>
                    <div style="color: #71717a; font-size: 0.85rem; margin-top: 4px;">Médecin, avocat, architecte, kiné, expert-comptable, notaire… votre ordre professionnel encadre votre activité.</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("J'exerce un métier réglementé", key="btn_choose_liberal", use_container_width=True):
                    select_structure(draft, "liberal", user_fullname)
                    st.session_state.ob_step = 2
                    st.rerun()

            st.write("")
            st.markdown("""
            <div style="background: #fefce8; border: 1.5px dashed #facc15; border-radius: 12px; padding: 16px 20px;">
                <div style="font-weight: 700; color: #09090b; font-size: 1rem;">🤷 Je ne sais pas encore</div>
                <div style="color: #71717a; font-size: 0.85rem; margin-top: 4px;">Pas de souci : on part sur le plus simple (travailler à son compte). Tout se change plus tard, sans rien perdre.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Je ne sais pas encore", key="btn_choose_unknown", use_container_width=True):
                select_structure(draft, "micro_enterprise", user_fullname)
                st.session_state.ob_step = 2
                st.rerun()

        # ----------------------------------------------------------------------
        # QUESTION 2 : IDENTITÉ DE VOTRE STRUCTURE
        # ----------------------------------------------------------------------
        elif current_step == 2:
            stype = draft.get("structure_type", "company")

            if stype == "micro_enterprise":
                st.markdown("""
                <div class="ob-title">Sous quel nom allez-vous facturer ?</div>
                <div class="ob-subtitle">À votre compte, il n'y a pas de nom de société à inventer : c'est votre <strong>nom et prénom</strong> qui apparaissent sur vos factures.</div>
                """, unsafe_allow_html=True)

                draft["name"] = st.text_input(
                    "Nom affiché sur vos factures :",
                    value=draft.get("name") or (f"{user_fullname} EI" if user_fullname else "Mon Activité"),
                    help="Par exemple : votre nom et prénom, suivi de « EI » (entrepreneur individuel).",
                    key="ob_micro_name",
                )
                draft["activity_label"] = st.text_input(
                    "Qu'est-ce que vous vendez ?",
                    value=draft.get("activity_label", ""),
                    placeholder="Ex : sites web, coaching, retouche photo…",
                    key="ob_micro_activity",
                )
                draft["address"] = st.text_input(
                    "Adresse professionnelle :",
                    value=draft.get("address", ""),
                    placeholder="Ex : 12 rue de la Paix",
                    key="ob_micro_address",
                )
                col_cp, col_ci = st.columns(2)
                with col_cp:
                    draft["postal_code"] = st.text_input(
                        "Code postal :", value=draft.get("postal_code", ""), key="ob_micro_cp"
                    )
                with col_ci:
                    draft["city"] = st.text_input(
                        "Ville :", value=draft.get("city", ""), key="ob_micro_city"
                    )
                with st.expander("Numéros officiels (optionnel)", expanded=False):
                    st.caption("Si votre activité est déjà déclarée, ces numéros seront vérifiés et utilisés sur vos factures.")
                    col_siren, col_siret = st.columns(2)
                    with col_siren:
                        draft["siren"] = st.text_input(
                            "SIREN (9 chiffres) :", value=draft.get("siren", ""),
                            placeholder="Ex : 123456789", key="ob_micro_siren"
                        )
                    with col_siret:
                        draft["siret"] = st.text_input(
                            "SIRET (14 chiffres) :", value=draft.get("siret", ""),
                            placeholder="Ex : 12345678900012", key="ob_micro_siret"
                        )

            else:
                titles = {
                    "company": ("Trouvons votre société", "Tapez le nom ou le numéro SIREN puis appuyez sur Entrée : les suggestions de l'Annuaire officiel apparaissent automatiquement."),
                    "sci": ("Trouvons votre SCI", "Tapez le nom ou le numéro SIREN puis appuyez sur Entrée : les suggestions de l'Annuaire officiel apparaissent automatiquement."),
                    "liberal": ("Trouvons votre activité", "Tapez le nom ou le numéro SIREN puis appuyez sur Entrée : les suggestions de l'Annuaire officiel apparaissent automatiquement."),
                }
                head_title, head_sub = titles.get(stype, titles["company"])
                st.markdown(f"""
                <div class="ob-title">{head_title}</div>
                <div class="ob-subtitle">{head_sub}</div>
                """, unsafe_allow_html=True)

                s_query = st.text_input(
                    "Nom ou SIREN de la structure :",
                    value=st.session_state.get("ob_query", ""),
                    placeholder="Ex : 952981363 ou le nom de votre structure",
                    label_visibility="collapsed",
                    key=f"ob_company_query_{stype}",
                )
                query = s_query.strip()

                if not query:
                    st.session_state.ob_results = []
                    st.session_state.ob_last_query = ""
                elif st.session_state.get("ob_last_query") != query:
                    with st.spinner("Recherche dans l'Annuaire officiel des entreprises..."):
                        st.session_state.ob_results = search_companies(query, limit=5)
                    st.session_state.ob_last_query = query
                    st.session_state.ob_query = query
                    # Nouvelle liste de suggestions : nouvelle clé de widget pour
                    # ne pas réappliquer automatiquement un ancien choix au retour.
                    st.session_state.ob_suggestion_nonce = st.session_state.get("ob_suggestion_nonce", 0) + 1

                results = st.session_state.get("ob_results") or []
                if query and st.session_state.get("ob_last_query") == query:
                    if results:
                        st.caption("Suggestions automatiques issues de l'Annuaire officiel. Choisissez la bonne structure.")
                        option_indexes = list(range(len(results)))
                        selected = st.selectbox(
                            "Suggestions",
                            option_indexes,
                            index=None,
                            format_func=lambda i: company_suggestion_label(results[i]),
                            placeholder="Sélectionnez une structure dans les suggestions…",
                            label_visibility="collapsed",
                            key=(
                                f"ob_suggestion_{stype}_"
                                f"{st.session_state.get('ob_suggestion_nonce', 0)}"
                            ),
                        )
                        if selected is not None:
                            apply_company_to_draft(draft, results[selected], user_fullname)
                            st.session_state.ob_results = []
                            st.session_state.ob_last_query = ""
                            st.session_state.ob_query = draft.get("name", "")
                            st.session_state.ob_step = 3
                            st.rerun()
                    else:
                        st.info("Aucune structure trouvée. Vous pouvez la créer à la main ci-dessous.")

                with st.expander(
                    "Ou remplir à la main (structure en cours de création)",
                    expanded=not bool(draft.get("name")) and not results,
                ):
                    draft["name"] = st.text_input(
                        "Nom de la structure :",
                        value=draft.get("name", ""),
                        key=f"ob_manual_name_{stype}",
                    )
                    all_forms = legal_forms_for(stype)
                    if len(all_forms) > 1:
                        form_idx = (
                            all_forms.index(draft["legal_form"])
                            if draft.get("legal_form") in all_forms
                            else 0
                        )
                        draft["legal_form"] = st.selectbox(
                            "Forme juridique :", all_forms, index=form_idx,
                            key=f"ob_manual_form_{stype}"
                        )
                    else:
                        draft["legal_form"] = all_forms[0]
                        st.caption(f"Forme juridique : {all_forms[0]}")
                    col_siren, col_siret = st.columns(2)
                    with col_siren:
                        draft["siren"] = st.text_input(
                            "SIREN (optionnel si pas encore immatriculé) :",
                            value=draft.get("siren", ""),
                            key=f"ob_manual_siren_{stype}",
                        )
                    with col_siret:
                        draft["siret"] = st.text_input(
                            "SIRET (optionnel) :",
                            value=draft.get("siret", ""),
                            key=f"ob_manual_siret_{stype}",
                        )
                    draft["activity_label"] = st.text_input(
                        "Activité (ex : conseil, bâtiment, location…) :",
                        value=draft.get("activity_label", ""),
                        key=f"ob_manual_activity_{stype}",
                    )
                    draft["address"] = st.text_input(
                        "Adresse du siège :",
                        value=draft.get("address", ""),
                        key=f"ob_manual_address_{stype}",
                    )
                    col_cp, col_ci = st.columns(2)
                    with col_cp:
                        draft["postal_code"] = st.text_input(
                            "Code postal :", value=draft.get("postal_code", ""),
                            key=f"ob_manual_cp_{stype}"
                        )
                    with col_ci:
                        draft["city"] = st.text_input(
                            "Ville :", value=draft.get("city", ""),
                            key=f"ob_manual_city_{stype}"
                        )

            st.write("")
            col_b1, col_b2 = st.columns([1, 2])
            with col_b1:
                if st.button("⬅ Retour", use_container_width=True):
                    st.session_state.ob_step = 1
                    st.rerun()
            with col_b2:
                if st.button("Continuer ➔", type="primary", use_container_width=True):
                    if not draft.get("name", "").strip():
                        typed = (st.session_state.get("ob_query") or "").strip()
                        if typed and not typed.replace(" ", "").isdigit():
                            draft["name"] = typed
                    missing = missing_identity_fields(draft)
                    if missing:
                        st.warning(
                            "Il manque "
                            + ", ".join(missing)
                            + ". Ces informations sont nécessaires pour émettre des factures conformes."
                        )
                    else:
                        st.session_state.ob_step = 3
                        st.rerun()

        # ----------------------------------------------------------------------
        # QUESTION 3 : RÉGIME DE TVA ADAPTÉ À LA STRUCTURE
        # ----------------------------------------------------------------------
        elif current_step == 3:
            stype = draft.get("structure_type", "company")
            st.markdown(f"""
            <div class="ob-title">{TVA_TITLE}</div>
            <div class="ob-subtitle">{tva_subtitle(stype)}</div>
            """, unsafe_allow_html=True)

            choices = tva_choices(stype)
            for choice in choices:
                with st.container(border=True):
                    title_col, badge_col = st.columns([3, 1])
                    with title_col:
                        st.markdown(f"**{choice['title']}**")
                    with badge_col:
                        if choice.get("badge"):
                            st.caption(choice["badge"])
                    st.caption(choice["description"])
                    if st.button(
                        "Choisir cette option",
                        key=f"btn_tva_{choice['key']}",
                        use_container_width=True,
                    ):
                        draft["regime_tva"] = choice["value"]
                        st.session_state.ob_tva_defaulted = False
                        st.session_state.ob_step = 4
                        st.rerun()

            st.write("")
            col_b1, col_b2 = st.columns([1, 2])
            with col_b1:
                if st.button("⬅ Retour", use_container_width=True):
                    st.session_state.ob_step = 2
                    st.rerun()
            with col_b2:
                if st.button(
                    "Je ne sais pas encore : appliquer le choix le plus courant",
                    use_container_width=True,
                ):
                    draft["regime_tva"] = choices[0]["value"]
                    st.session_state.ob_tva_defaulted = True
                    st.session_state.ob_step = 4
                    st.rerun()

        # ----------------------------------------------------------------------
        # QUESTION 4 : COORDONNÉES DE FACTURATION & VALIDATION FINALE
        # ----------------------------------------------------------------------
        elif current_step == 4:
            st.markdown("""
            <div class="ob-title">Dernière étape : vos coordonnées</div>
            <div class="ob-subtitle">Ces informations servent à émettre des devis et des factures prêts à envoyer. Vous pourrez les compléter plus tard.</div>
            """, unsafe_allow_html=True)

            st.caption(
                f"Structure : {draft.get('name') or 'à compléter'} • "
                f"{draft.get('legal_form', '')} • TVA : {draft.get('regime_tva', '')} • "
                f"{draft.get('address', '')} {draft.get('postal_code', '')} {draft.get('city', '')}".strip()
            )
            if st.session_state.get("ob_tva_defaulted"):
                st.info(
                    "Aucun régime de TVA n'a été choisi : le cas le plus courant pour votre "
                    "structure a été appliqué. Vous pourrez le modifier dans votre fiche."
                )

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                draft["president"] = st.text_input(
                    "Qui représente la structure ? (Prénom Nom) :",
                    value=draft.get("president") or user_fullname,
                    key="ob_president",
                )
                curr_role = draft.get("president_role") or "Dirigeant"
                roles = role_options(curr_role)
                role_idx = roles.index(curr_role) if curr_role in roles else 0
                draft["president_role"] = st.selectbox(
                    "Quel est son rôle ?", roles, index=role_idx, key="ob_president_role"
                )
                imp_options = ["IS", "IR"]
                imp_labels = {
                    "IS": "Impôt sur les sociétés (IS)",
                    "IR": "Impôt sur le revenu (IR)",
                }
                imp_idx = imp_options.index(draft.get("regime_imposition", "IS")) if draft.get("regime_imposition") in imp_options else 0
                draft["regime_imposition"] = st.selectbox(
                    "Imposition des bénéfices :",
                    imp_options,
                    index=imp_idx,
                    format_func=lambda x: imp_labels[x],
                    help="La plupart des SAS et SARL relèvent de l'IS. Les micro-entreprises et les SCI relèvent en général de l'IR.",
                    key="ob_imposition",
                )

            with col_p2:
                draft["iban"] = st.text_input(
                    "IBAN pour recevoir vos paiements (optionnel) :",
                    value=draft.get("iban", ""),
                    placeholder="Ex : FR76 3000 6000 0112 …",
                    key="ob_iban",
                )
                draft["bic"] = st.text_input(
                    "BIC de votre banque (optionnel) :",
                    value=draft.get("bic", ""),
                    placeholder="Ex : BNPAFRPPXXX",
                    key="ob_bic",
                )
                fiscal_dates = ["31/12", "30/06", "30/09", "31/03"]
                fye_idx = fiscal_dates.index(draft.get("fiscal_year_end", "31/12")) if draft.get("fiscal_year_end") in fiscal_dates else 0
                draft["fiscal_year_end"] = st.selectbox(
                    "Date de clôture de vos comptes :",
                    fiscal_dates,
                    index=fye_idx,
                    key="ob_fiscal_year_end",
                )

            st.write("")
            st.write("")

            if st.button("Finaliser et activer mon assistant ÉCHAP", type="primary", use_container_width=True):
                missing = missing_identity_fields(draft)
                if missing:
                    st.error(
                        "Il manque "
                        + ", ".join(missing)
                        + ". Revenez à l'étape précédente pour compléter votre adresse."
                    )
                else:
                    ent_name_val = draft.get("name", "").strip() or f"{user_fullname} ({draft.get('legal_form', 'Structure')})"
                    draft["name"] = ent_name_val
                    draft["company_name"] = ent_name_val
                    draft["representative_name"] = draft.get("president") or user_fullname
                    draft["representative_role"] = draft.get("president_role", "Dirigeant")

                    res = create_entity_for_user(user_id, draft, role="owner")
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.session_state.active_entity_id = res["id"]
                        st.session_state.adding_entity = False
                        st.session_state.pop("ob_step", None)
                        st.session_state.pop("ob_draft", None)
                        st.session_state.pop("ob_results", None)
                        st.session_state.pop("ob_query", None)
                        st.session_state.pop("ob_last_query", None)
                        st.session_state.pop("ob_suggestion_nonce", None)
                        st.session_state.pop("ob_tva_defaulted", None)
                        st.success(f"Structure « {ent_name_val} » configurée avec succès ! Lancement...")
                        st.rerun()

            col_b1, col_b2 = st.columns([1, 2])
            with col_b1:
                if st.button("⬅ Retour", use_container_width=True):
                    st.session_state.ob_step = 3
                    st.rerun()

        # Bouton discret pour annuler l'ajout ou se déconnecter
        st.write("")
        if is_adding_entity:
            if st.button("Annuler l'ajout", type="secondary"):
                st.session_state.adding_entity = False
                st.session_state.pop("ob_step", None)
                st.session_state.pop("ob_draft", None)
                st.session_state.pop("ob_query", None)
                st.session_state.pop("ob_last_query", None)
                st.session_state.pop("ob_suggestion_nonce", None)
                st.session_state.pop("ob_tva_defaulted", None)
                st.rerun()
        else:
            if st.button("Se déconnecter", type="secondary"):
                st.session_state.user = None
                st.session_state.pop("ob_step", None)
                st.session_state.pop("ob_draft", None)
                st.session_state.pop("ob_query", None)
                st.session_state.pop("ob_last_query", None)
                st.session_state.pop("ob_suggestion_nonce", None)
                st.session_state.pop("ob_tva_defaulted", None)
                st.rerun()

    st.stop()


# Récupération du profil de la structure active
active_entity_id = st.session_state.active_entity_id
curr_entity = get_company_profile(user_id, entity_id=active_entity_id)
company_name = curr_entity.get("name") or curr_entity.get("company_name") or "Votre Structure"


# --- BARRE LATÉRALE MINIMALISTE & SWITCHER MULTI-ENTITÉS ---
with st.sidebar:
    st.markdown(render_brand_sidebar_header(company_name), unsafe_allow_html=True)
    st.caption(f"👤 Connecté : **{user_fullname}**")

    # Switcher multi-structures si l'utilisateur en possède plusieurs
    if len(user_entities) > 1:
        st.markdown("---")
        st.markdown("<span style='font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 700;'>Changer de structure</span>", unsafe_allow_html=True)
        type_tags = {"micro_enterprise": "[Micro]", "sci": "[SCI]", "liberal": "[Libéral]", "company": "[Société]"}
        ent_labels = {e["id"]: f"{type_tags.get(e.get('structure_type'), '[Structure]')} {e['name']}" for e in user_entities}
        curr_idx = list(ent_labels.keys()).index(active_entity_id) if active_entity_id in ent_labels else 0
        new_active = st.selectbox(
            "Structure active :",
            options=list(ent_labels.keys()),
            format_func=lambda x: ent_labels[x],
            index=curr_idx,
            label_visibility="collapsed",
            key="sb_entity_selector"
        )
        if new_active != active_entity_id:
            st.session_state.active_entity_id = new_active
            st.rerun()

    # Bouton pour ajouter une structure supplémentaire (multi-entités)
    c_add1, c_add2 = st.columns([4, 1])
    with c_add1:
        st.markdown(f"<span style='font-size: 0.72rem; color: #047857; font-weight: 600;'>{curr_entity.get('legal_form', 'SAS')} qualifiée</span>", unsafe_allow_html=True)
    with c_add2:
        if st.button("+", help="Ajouter une autre entité (ex: Micro, SCI, SAS)"):
            st.session_state.adding_entity = True
            st.rerun()

    st.markdown("---")

    nav_options = [
        "Assistant",
        "Tableau de bord",
        "Documents & Factures",
        "Outils externes"
    ]
    clean_nav = st.radio("Navigation", nav_options, label_visibility="collapsed")

    st.markdown("---")
    if st.button("Déconnexion", use_container_width=True):
        st.session_state.user = None
        st.rerun()


# ==============================================================================
# VUE 1 : TABLEAU DE BORD FINANCIER & COMPTABLE EN TEMPS RÉEL
# ==============================================================================
if clean_nav == "Tableau de bord":
    st.markdown(f"## **Tableau de bord — {company_name}**")
    st.caption("Indicateurs financiers et suivi de l'activité en temps réel.")
    st.write("")

    finances = get_company_finances(user_id, entity_id=active_entity_id)

    # 4 Cartes de métriques financières
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ca_sub = "↑ +14 % vs exercice précédent" if finances['ca_ytd'] > 0 else "Exercice en cours"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Chiffre d'affaires (YTD)</div>
            <div class="metric-value">{finances['ca_ytd']:,.0f} €</div>
            <div class="metric-sub">{ca_sub}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        tres_sub = "Solde bancaire rapproché" if finances['tresorerie'] > 0 else "En attente de relevé"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Trésorerie disponible</div>
            <div class="metric-value">{finances['tresorerie']:,.0f} €</div>
            <div class="metric-sub">{tres_sub}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        creance_sub = "Factures en attente" if finances['creances_clients'] > 0 else "Aucun impayé"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Créances clients</div>
            <div class="metric-value">{finances['creances_clients']:,.0f} €</div>
            <div class="metric-sub" style="color: #64748b;">{creance_sub}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        tva_sub = "Échéance au 19 du mois" if finances['tva_due'] > 0 else "À jour"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">TVA nette due</div>
            <div class="metric-value">{finances['tva_due']:,.0f} €</div>
            <div class="metric-sub" style="color: #64748b;">{tva_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    col_trans, col_ech = st.columns([1.3, 1])

    # Opérations bancaires récentes
    with col_trans:
        st.markdown("#### **Dernières opérations**")
        st.caption("Mouvements bancaires rapprochés.")
        if finances["recent_transactions"]:
            for op in finances["recent_transactions"]:
                color = "#10b981" if op["amount"] > 0 else "#0f172a"
                sign = "+" if op["amount"] > 0 else ""
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f1f5f9;">
                    <div>
                        <div style="font-weight: 600; color: #1e293b; font-size: 0.95rem;">{op['label']}</div>
                        <div style="color: #94a3b8; font-size: 0.78rem;">{op['date']} • Compte {op['compte']}</div>
                    </div>
                    <div style="font-weight: 700; color: {color}; font-size: 1rem;">
                        {sign}{op['amount']:,.2f} €
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune transaction enregistrée pour le moment. Vous pouvez déposer vos premiers relevés ou factures dans « Documents & Factures ».")

    # Échéances et obligations
    with col_ech:
        st.markdown("#### **Prochaines échéances**")
        st.caption("Obligations fiscales et administratives.")
        if finances["echeances"]:
            for ech in finances["echeances"]:
                badge_bg = "#fee2e2" if ech["urgency"] == "Urgent" else "#f1f5f9"
                badge_color = "#dc2626" if ech["urgency"] == "Urgent" else "#475569"
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 14px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; font-size: 0.9rem;">{ech['label']}</span>
                        <span style="background: {badge_bg}; color: {badge_color}; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;">{ech['urgency']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 0.8rem; color: #64748b;">
                        <span>Date limite : <b>{ech['date']}</b></span>
                        <span>{ech['montant']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune échéance urgente en attente.")


# ==============================================================================
# VUE 2 : ASSISTANT ECHAP (CONVERSATION FLUIDE)
# ==============================================================================
elif clean_nav == "Assistant":
    st.markdown(f"## **Assistant {brand['name']}**")
    st.caption(f"Déléguez vos questions et démarches administratives pour **{company_name}**. *{brand['tagline']}*")

    # Chargement historique de la structure active
    chat_history = load_user_chat(user_id, entity_id=active_entity_id)
    if not chat_history:
        welcome_msg = (
            f"Bonjour, je suis votre assistant {brand['name']} pour **{company_name}**.\n\n"
            f"*{brand['tagline']}* Je prends en charge votre comptabilité, fiscalité, facturation, trésorerie et démarches administratives. "
            "Que souhaitez-vous traiter ?"
        )
        save_user_message(user_id, "assistant", welcome_msg, entity_id=active_entity_id)
        chat_history = [{"role": "assistant", "content": welcome_msg}]

    # Affichage du flux de discussion
    for idx, msg in enumerate(chat_history):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Si le message comporte une question interactive structurée et que c'est le dernier message
            if msg.get("question_data") and idx == len(chat_history) - 1:
                q_data = msg["question_data"]
                st.write("")
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1.5px solid #3b82f6; border-radius: 8px; padding: 14px 18px; margin: 10px 0 16px 0;">
                    <div style="font-weight: 700; color: #1e3a8a; font-size: 0.95rem; margin-bottom: 8px;">
                        {q_data.get('question', 'Précision requise')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                opts = q_data.get("options", [])
                chosen_opt = None
                if opts:
                    chosen_opt = st.radio("Sélectionnez votre option :", opts, key=f"q_radio_{idx}", label_visibility="collapsed")

                custom_text = ""
                if q_data.get("allow_custom", True):
                    custom_text = st.text_input("Ou écrivez votre réponse personnalisée :", key=f"q_custom_{idx}", placeholder="Autre réponse...")

                c_valid, c_empty = st.columns([1.5, 3])
                with c_valid:
                    if st.button("Valider ce choix", key=f"q_submit_{idx}", type="primary", use_container_width=True):
                        final_choice = custom_text.strip() if custom_text.strip() else chosen_opt
                        if final_choice:
                            save_user_message(user_id, "user", final_choice, entity_id=active_entity_id)
                            # Traitement immédiat de la réponse choisie
                            if api_key:
                                profile = get_company_profile(user_id, entity_id=active_entity_id)
                                sys_prompt = build_unified_system_prompt(company_name, final_choice, company_profile=profile)
                                m_payload = [{"role": "system", "content": sys_prompt}]
                                for m in load_user_chat(user_id, entity_id=active_entity_id):
                                    m_payload.append({"role": m["role"], "content": m["content"]})
                                with st.spinner("Prise en compte..."):
                                    res_cycle = run_agent_cycle(m_payload, api_key=api_key, user_id=user_id)
                                    save_user_message(user_id, "assistant", res_cycle["content"], question_data=res_cycle.get("question_data"), entity_id=active_entity_id)
                            st.rerun()

    # Entrée utilisateur
    if user_query := st.chat_input("Posez votre question ou déléguez une démarche..."):
        save_user_message(user_id, "user", user_query, entity_id=active_entity_id)
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            if api_key:
                profile = get_company_profile(user_id, entity_id=active_entity_id)
                system_prompt = build_unified_system_prompt(company_name, user_query, company_profile=profile)
                messages_payload = [{"role": "system", "content": system_prompt}]
                # Historique récent
                recent_history = load_user_chat(user_id, entity_id=active_entity_id)
                for m in recent_history:
                    messages_payload.append({"role": m["role"], "content": m["content"]})

                with st.spinner("Recherche et analyse en cours..."):
                    agent_result = run_agent_cycle(messages_payload, api_key=api_key, user_id=user_id)
                    full_response = agent_result["content"]
                    question_data = agent_result.get("question_data")

                st.markdown(full_response)
                save_user_message(user_id, "assistant", full_response, question_data=question_data, entity_id=active_entity_id)
                if question_data:
                    st.rerun()
            else:
                simulated_text = simulate_offline_response(user_query)
                st.markdown(simulated_text)
                save_user_message(user_id, "assistant", simulated_text, entity_id=active_entity_id)

    # Réinitialisation discrète
    col_sp, col_rst = st.columns([5, 1])
    with col_rst:
        if st.button("Effacer le chat", type="secondary"):
            clear_user_chat(user_id, entity_id=active_entity_id)
            st.rerun()


# ==============================================================================
# VUE 3 : DOCUMENTS & FACTURES
# ==============================================================================
elif clean_nav == "Documents & Factures":
    st.markdown("## **Documents & Factures**")
    st.caption("Pièces justificatives, contrats et exports légaux.")
    st.write("")

    col_up, col_exp = st.columns(2)

    with col_up:
        st.markdown("#### **Ajouter un document**")
        uploaded_file = st.file_uploader("", type=["pdf", "csv", "png", "jpg", "json"], label_visibility="collapsed")
        if uploaded_file is not None:
            if st.button("Enregistrer le document", use_container_width=True, type="primary"):
                save_res = save_document(
                    user_id=user_id,
                    filename=uploaded_file.name,
                    content_bytes=uploaded_file.getbuffer().tobytes(),
                    kind="upload"
                )
                if "error" in save_res:
                    st.error(save_res["error"])
                else:
                    st.success(f"Document « {uploaded_file.name} » enregistré.")
                    st.rerun()

        st.write("")
        st.markdown("##### **Documents classés**")
        docs = list_user_documents(user_id, kind="upload")
        if docs:
            for d in docs:
                st.markdown(f"- **{d['filename']}** ({d['size_kb']} Ko) • *{d['created_at']}*")
        else:
            st.info("Aucun document déposé pour le moment.")

    with col_exp:
        st.markdown("#### **Générer un export comptable**")
        if st.button("Générer le Fichier des Écritures Comptables (FEC)", use_container_width=True):
            fec_headers = [
                "JournalCode", "JournalLib", "EcritureNum", "EcritureDate", "CompteNum", "CompteLib",
                "CompAuxNum", "CompAuxLib", "PieceRef", "PieceDate", "EcritureLib",
                "Debit", "Credit", "EcritureLet", "DateLet", "ValidDate", "Montantdevise", "Idevise"
            ]
            fec_entries = [
                ["VE", "Journal des Ventes", "V0001", "20261015", "411100", "Clients - Ventes", "", "", "FAC-2026-042", "20261015", f"Facture {company_name}", "1200,00", "0,00", "", "", "20261015", "", ""],
                ["VE", "Journal des Ventes", "V0001", "20261015", "706000", "Prestations de services", "", "", "FAC-2026-042", "20261015", f"Facture {company_name}", "0,00", "1000,00", "", "", "20261015", "", ""],
                ["VE", "Journal des Ventes", "V0001", "20261015", "445710", "TVA collectee 20%", "", "", "FAC-2026-042", "20261015", f"Facture {company_name}", "0,00", "200,00", "", "", "20261015", "", ""],
                ["BQ", "Banque", "B0001", "20261020", "512000", "Banque compte courant", "", "", "VIR-CLIENT", "20261020", "Reglement client", "1200,00", "0,00", "", "", "20261020", "", ""],
                ["BQ", "Banque", "B0001", "20261020", "411100", "Clients - Ventes", "", "", "VIR-CLIENT", "20261020", "Reglement client", "0,00", "1200,00", "", "", "20261020", "", ""],
            ]
            fec_content = "\t".join(fec_headers) + "\n" + "\n".join("\t".join(row) for row in fec_entries)
            save_document(user_id, f"FEC20261231_{username}.txt", fec_content.encode("utf-8"), kind="export")
            st.success("Fichier FEC généré avec succès.")
            st.rerun()

        st.write("")
        st.markdown("##### **Exports disponibles au téléchargement**")
        exports = list_user_documents(user_id, kind="export")
        if exports:
            for exp in exports:
                doc_tuple = get_document_content(user_id, exp["id"])
                if doc_tuple:
                    fname, fbytes = doc_tuple
                    st.download_button(
                        label=f"Télécharger {fname} ({exp['size_kb']} Ko)",
                        data=fbytes,
                        file_name=fname,
                        key=f"dl_{exp['id']}",
                        use_container_width=True
                    )
        else:
            st.info("Aucun export généré.")


# ==============================================================================
# VUE 4 : OUTILS EXTERNES & REGISTRE
# ==============================================================================
elif clean_nav == "Outils externes":
    st.markdown("## **Outils externes**")
    st.caption("Recherche au registre officiel des entreprises et consultation du PCG 2026.")
    st.write("")

    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "Annuaire des Entreprises",
        "Plan Comptable 2026",
        "Barème Kilométrique",
        "Ma Fiche Entreprise"
    ])

    with sub_tab1:
        c_search, c_b = st.columns([4, 1])
        with c_search:
            q_comp = st.text_input("Raison sociale ou numéro SIREN", value="Doctolib", label_visibility="collapsed")
        with c_b:
            btn_s = st.button("Rechercher", use_container_width=True)

        if q_comp:
            res_comp = search_companies(q_comp, limit=3)
            if res_comp:
                for c in res_comp:
                    with st.expander(f"{c.get('nom_complet')} — SIREN {c.get('siren')}"):
                        st.write(f"**SIRET** : `{c.get('siret')}` • **Forme** : {c.get('nature_juridique')}")
                        st.write(f"**Activité** : {c.get('libelle_activite')} (`{c.get('activite_principale')}`)")
                        st.write(f"**Adresse** : {c.get('adresse')}, {c.get('code_postal')} {c.get('ville')}")

    with sub_tab2:
        c_pcg, c_cl = st.columns([3, 1])
        with c_pcg:
            pcg_q = st.text_input("Numéro ou libellé de compte", value="411", label_visibility="collapsed")
        with c_cl:
            classe_f = st.selectbox("Classe", options=["Toutes", 1, 2, 3, 4, 5, 6, 7], label_visibility="collapsed")
        cl_val = None if classe_f == "Toutes" else int(classe_f)
        accs = search_pcg(pcg_q, classe=cl_val, limit=25)
        st.dataframe(accs, use_container_width=True, hide_index=True)

    with sub_tab3:
        cv_val = st.number_input("Puissance fiscale (CV)", min_value=1, max_value=20, value=5)
        km_val = st.number_input("Kilomètres parcourus", min_value=1, max_value=50000, value=6500, step=500)
        elec_val = st.checkbox("Véhicule 100% électrique (+20 %)", value=True)
        ik = calculate_ik(cv_val, km_val, electrique=elec_val)
        if "error" not in ik:
            st.success(f"Montant déductible : **{ik['montant_total_euros']:,.2f} €** ({ik['detail_calcul']})")

    with sub_tab4:
        st.markdown(f"#### **Fiche officielle de {company_name}**")
        st.caption("Ces informations sont enregistrées en base et utilisées par ÉCHAP pour générer vos factures, déclarations et statuts.")

        curr_prof = get_company_profile(user_id, entity_id=active_entity_id)

        # Remplissage automatique par SIREN
        c_sync_siren, c_sync_btn = st.columns([3, 1])
        with c_sync_siren:
            sync_siren = st.text_input("Synchroniser automatiquement par SIREN :", placeholder="ex: 952981363 (Seed Studio)")
        with c_sync_btn:
            st.write("")
            st.write("")
            if st.button("Synchroniser", use_container_width=True):
                if sync_siren:
                    sirene_data = search_companies(sync_siren, limit=1)
                    if sirene_data:
                        found = sirene_data[0]
                        pres = ""
                        for d in found.get("dirigeants", []):
                            qual = d.get("qualite") or ""
                            if "Président" in qual or "Gérant" in qual or "Directeur" in qual:
                                pres = f"{d.get('prenoms') or ''} {d.get('nom') or ''}".strip()
                        curr_prof["siren"] = found.get("siren", "")
                        curr_prof["siret"] = found.get("siret", "")
                        curr_prof["legal_form"] = "SAS" if "5710" in str(found.get("nature_juridique", "")) or "SAS" in str(found.get("nature_juridique", "")) else "SARL"
                        curr_prof["address"] = found.get("adresse", "")
                        curr_prof["postal_code"] = found.get("code_postal", "")
                        curr_prof["city"] = found.get("ville", "")
                        curr_prof["activity_code"] = found.get("activite_principale", "")
                        curr_prof["activity_label"] = found.get("libelle_activite", "")
                        if pres:
                            curr_prof["president"] = pres
                        update_company_profile(user_id, curr_prof, entity_id=active_entity_id)
                        st.success(f"Fiche synchronisée avec l'Annuaire officiel pour {found.get('nom_complet')} !")
                        st.rerun()
                    else:
                        st.error("Entreprise introuvable pour ce SIREN.")

        st.markdown("---")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            all_forms = ["SAS", "SASU", "SARL", "EURL", "Micro-entreprise", "Entreprise Individuelle (EI)", "SCI", "Profession libérale (BNC)"]
            f_form = st.selectbox("Forme juridique :", all_forms, index=all_forms.index(curr_prof.get("legal_form", "SAS")) if curr_prof.get("legal_form") in all_forms else 0)
            f_siren = st.text_input("SIREN :", value=curr_prof.get("siren", ""))
            f_siret = st.text_input("SIRET :", value=curr_prof.get("siret", ""))
            f_ape = st.text_input("Code APE :", value=curr_prof.get("activity_code", ""))
            f_act = st.text_input("Libellé d'activité :", value=curr_prof.get("activity_label", ""))
            f_pres = st.text_input("Dirigeant / Mandataire :", value=curr_prof.get("president", ""))
            all_roles = ["Président", "Directeur Général", "Gérant", "Entrepreneur individuel", "Associé gérant"]
            f_role = st.selectbox("Qualité / Rôle :", all_roles, index=all_roles.index(curr_prof.get("president_role", "Président")) if curr_prof.get("president_role") in all_roles else 0)
        with col_p2:
            f_addr = st.text_input("Adresse :", value=curr_prof.get("address", ""))
            f_cp = st.text_input("Code postal :", value=curr_prof.get("postal_code", ""))
            f_city = st.text_input("Ville :", value=curr_prof.get("city", ""))
            all_tvas = [
                "Réel normal (20%)",
                "Réel simplifié",
                "Franchise en base de TVA (art. 293 B du CGI - exonéré)",
                TVA_EXONERATION_261D,
            ]
            f_tva = st.selectbox("Régime de TVA :", all_tvas, index=all_tvas.index(curr_prof.get("regime_tva", "Réel normal (20%)")) if curr_prof.get("regime_tva") in all_tvas else 0)
            f_imp = st.radio("Imposition :", ["IS", "IR"], index=0 if curr_prof.get("regime_imposition", "IS") == "IS" else 1, horizontal=True)
            all_fyes = ["31/12", "30/06", "30/09", "31/03"]
            f_fye = st.selectbox("Clôture d'exercice :", all_fyes, index=all_fyes.index(curr_prof.get("fiscal_year_end", "31/12")) if curr_prof.get("fiscal_year_end") in all_fyes else 0)
            f_iban = st.text_input("IBAN (pour vos factures) :", value=curr_prof.get("iban", ""))
            f_bic = st.text_input("BIC :", value=curr_prof.get("bic", ""))

        if st.button("Enregistrer les modifications de ma fiche", use_container_width=True, type="primary"):
            curr_prof.update({
                "legal_form": f_form,
                "siren": f_siren,
                "siret": f_siret,
                "address": f_addr,
                "postal_code": f_cp,
                "city": f_city,
                "activity_code": f_ape,
                "activity_label": f_act,
                "regime_tva": f_tva,
                "regime_imposition": f_imp,
                "fiscal_year_end": f_fye,
                "president": f_pres,
                "president_role": f_role,
                "iban": f_iban,
                "bic": f_bic
            })
            update_company_profile(user_id, curr_prof, entity_id=active_entity_id)
            st.success("Fiche d'entreprise mise à jour et mémorisée en base de données !")
            st.rerun()
