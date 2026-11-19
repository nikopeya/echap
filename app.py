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

        auth_mode = st.radio("Mode d'accès", ["Connexion", "Créer un compte"], horizontal=True, label_visibility="collapsed")

        if auth_mode == "Connexion":
            username = st.text_input("Identifiant", key="login_username", placeholder="Votre identifiant")
            password = st.text_input("Mot de passe", type="password", key="login_password", placeholder="Votre mot de passe")
            st.write("")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Se connecter", use_container_width=True, type="primary"):
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Identifiant ou mot de passe incorrect.")
            with col_b2:
                if st.button("⚡ Accès démo", use_container_width=True):
                    demo_user = authenticate_user("testeur1", "test1234")
                    if demo_user:
                        st.session_state.user = demo_user
                        st.rerun()
            st.caption("Comptes : `testeur1`, `testeur2`, `testeur3` (mot de passe: `test1234`)")

        else:
            reg_name = st.text_input("Prénom et Nom", placeholder="Ex : Alexandre Martin")
            reg_user = st.text_input("Identifiant", placeholder="Identifiant souhaité")
            reg_pass = st.text_input("Mot de passe", type="password", placeholder="Mot de passe")
            st.write("")
            if st.button("Créer mon compte", use_container_width=True, type="primary"):
                res = register_user(reg_user, reg_pass, full_name=reg_name)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.session_state.user = res
                    st.rerun()

    st.stop()


# ==============================================================================
# 2. ESPACE CONNECTÉ (UTILISATEUR & STRUCTURES)
# ==============================================================================
user = st.session_state.user
user_id = user["id"]
user_fullname = user.get("full_name") or user.get("username")
username = user["username"]

# Récupération des structures associées à l'utilisateur
user_entities = get_user_entities(user_id)

# Gestion de l'entité active
if "active_entity_id" not in st.session_state or not any(e["id"] == st.session_state.active_entity_id for e in user_entities):
    st.session_state.active_entity_id = user_entities[0]["id"] if user_entities else None

active_entity_id = st.session_state.active_entity_id
is_adding_entity = st.session_state.get("adding_entity", False)

# ==============================================================================
# ONBOARDING / AJOUT DE STRUCTURE (SI AUCUNE STRUCTURE OU DEMANDE D'AJOUT)
# ==============================================================================
if not user_entities or is_adding_entity:
    title_action = "Ajouter une nouvelle structure" if user_entities else "Bienvenue sur ÉCHAP"
    sub_action = (
        "Vous pouvez piloter plusieurs entités (auto-entreprise, SAS, SCI) depuis votre compte unique."
        if user_entities
        else "Configurons votre première structure d'activité. Votre assistant ÉCHAP utilise ces données pour votre facturation légale, votre calendrier et vos démarches administratives."
    )

    st.markdown(f"""
    <div style="text-align: center; max-width: 740px; margin: 1.5rem auto 2rem auto;">
        <span style="background: #eef2ff; color: #4338ca; font-size: 0.8rem; font-weight: 700; padding: 5px 14px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em;">Structure & Fiscalité</span>
        <h1 style="font-size: 2.2rem; font-weight: 800; color: #0f172a; margin-top: 12px; margin-bottom: 8px;">{title_action}</h1>
        <p style="color: #64748b; font-size: 1.02rem; line-height: 1.5;">{sub_action}</p>
    </div>
    """, unsafe_allow_html=True)

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

    # --- ÉTAPE 1 : TYPE DE STRUCTURE & DÉNOMINATION ---
    st.markdown("### **1. Type d'activité & Structure juridique**")
    st.caption("Sélectionnez le type de structure pour adapter immédiatement les règles fiscales.")

    type_options = {
        "micro_enterprise": "Auto-entrepreneur / Micro-entreprise (Entreprise Individuelle sans société)",
        "company": "Société commerciale (SAS, SASU, SARL, EURL)",
        "sci": "Société Civile Immobilière (SCI)",
        "liberal": "Profession libérale (BNC / Activité indépendante réglementée)"
    }
    selected_stype = st.radio(
        "Type de structure :",
        options=list(type_options.keys()),
        format_func=lambda k: type_options[k],
        horizontal=False,
        key="ob_stype_radio"
    )
    draft["structure_type"] = selected_stype

    # Pré-réglages intelligents selon le type
    if selected_stype == "micro_enterprise":
        default_name = f"{user_fullname} EI" if user_fullname else "Mon Activité Indépendante"
        if not draft.get("name") or draft.get("name") == "Mon Entreprise":
            draft["name"] = default_name
        draft["legal_form"] = "Micro-entreprise"
        draft["regime_tva"] = "Franchise en base de TVA (art. 293 B du CGI - exonéré)"
        draft["regime_imposition"] = "IR"
        draft["president_role"] = "Entrepreneur individuel"
        st.info("**Indépendants & Auto-entrepreneurs :** Vous n'avez pas besoin d'un nom de société. Votre dénomination légale officielle est simplement votre Nom et Prénom (avec mention 'EI'). Vous bénéficiez de la franchise de TVA (art. 293 B) par défaut.")
    elif selected_stype == "sci":
        draft["legal_form"] = "SCI"
        draft["president_role"] = "Gérant"
    elif selected_stype == "liberal":
        draft["legal_form"] = "Profession libérale (BNC)"
        draft["regime_imposition"] = "IR"
        draft["president_role"] = "Titulaire libéral"

    st.write("")

    # Recherche officielle par SIREN ou Nom (facultatif si micro sans SIREN immédiat)
    st.markdown("#### **Identification officielle (Registre INSEE / Annuaire des Entreprises)**")
    c_sq, c_sb = st.columns([4, 1])
    with c_sq:
        q_search = st.text_input(
            "Numéro SIREN (9 chiffres) ou raison sociale (optionnel) :",
            value="",
            placeholder="Ex : 952981363 ou Doctolib ou nom commercial",
            key="ob_search_input"
        )
    with c_sb:
        st.write("")
        st.write("")
        btn_search = st.button("Rechercher", use_container_width=True)

    if q_search and btn_search:
        with st.spinner("Recherche au registre officiel..."):
            st.session_state.ob_results = search_companies(q_search, limit=3)

    if st.session_state.get("ob_results"):
        st.markdown("##### Entreprises officielles trouvées :")
        for idx, comp in enumerate(st.session_state.ob_results):
            nat = str(comp.get("nature_juridique") or "")
            det_form = "SAS"
            if "5710" in nat or "SAS" in nat:
                det_form = "SAS"
            elif "SARL" in nat:
                det_form = "SARL"
            elif "1000" in nat or "Entrepreneur" in nat:
                det_form = "Micro-entreprise"
            elif "SCI" in nat or "Société civile" in nat:
                det_form = "SCI"

            pres_cand = ""
            for d in comp.get("dirigeants", []):
                # Utiliser (d.get("qualite") or "") pour éviter le TypeError: NoneType
                if any(k in (d.get("qualite") or "") for k in ["Président", "Gérant", "Directeur", "Entrepreneur"]):
                    pres_cand = f"{d.get('prenoms') or ''} {d.get('nom') or ''}".strip()
                    break

            with st.container():
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span style="font-weight: 700; font-size: 1rem; color: #0f172a;">{comp.get('nom_complet')}</span>
                        <span style="font-family: monospace; font-size: 0.85rem; color: #475569;">SIREN {comp.get('siren')}</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">
                        📍 {comp.get('adresse', '')}, {comp.get('code_postal', '')} {comp.get('ville', '')} • Activité : {comp.get('libelle_activite') or comp.get('activite_principale', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"⚡ Remplir avec « {comp.get('nom_complet')} »", key=f"sel_comp_{idx}", use_container_width=True):
                    draft["name"] = comp.get("nom_complet", "")
                    draft["siren"] = comp.get("siren", "")
                    draft["siret"] = comp.get("siret", "")
                    draft["legal_form"] = det_form
                    draft["address"] = comp.get("adresse", "")
                    draft["postal_code"] = comp.get("code_postal", "")
                    draft["city"] = comp.get("ville", "")
                    draft["activity_code"] = comp.get("activite_principale", "")
                    draft["activity_label"] = comp.get("libelle_activite", "")
                    if pres_cand:
                        draft["president"] = pres_cand
                    st.session_state.ob_results = None
                    st.success("Informations officielles renseignées !")
                    st.rerun()

    with st.expander("Détails d'identification de la structure", expanded=True):
        c_i1, c_i2 = st.columns(2)
        with c_i1:
            lbl_name = "Nom ou Dénomination officielle :" if selected_stype != "micro_enterprise" else "Nom de votre activité / EI :"
            draft["name"] = st.text_input(lbl_name, value=draft.get("name", ""))
            draft["siren"] = st.text_input("Numéro SIREN (9 chiffres, optionnel si en création) :", value=draft.get("siren", ""))
            draft["siret"] = st.text_input("Numéro SIRET du siège (14 chiffres) :", value=draft.get("siret", ""))
            draft["activity_code"] = st.text_input("Code APE / NAF :", value=draft.get("activity_code", ""), placeholder="Ex: 62.01Z")
        with c_i2:
            draft["address"] = st.text_input("Adresse professionnelle ou siège :", value=draft.get("address", ""))
            draft["postal_code"] = st.text_input("Code postal :", value=draft.get("postal_code", ""))
            draft["city"] = st.text_input("Ville :", value=draft.get("city", ""))
            draft["activity_label"] = st.text_input("Description de l'activité :", value=draft.get("activity_label", ""), placeholder="Ex: Prestations de conseil")

    st.write("")

    # --- ÉTAPE 2 : STATUT & FISCALITÉ ---
    st.markdown("### **2. Forme juridique, Fiscalité & TVA**")
    st.caption("Ces règles permettent à ÉCHAP d'appliquer le bon régime de TVA et d'adapter votre calendrier légal.")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        legal_forms = ["SAS", "SASU", "SARL", "EURL", "Micro-entreprise", "Entreprise Individuelle (EI)", "SCI", "Profession libérale (BNC)"]
        curr_form = draft.get("legal_form", "SAS")
        form_idx = legal_forms.index(curr_form) if curr_form in legal_forms else 0
        draft["legal_form"] = st.selectbox("Forme juridique :", legal_forms, index=form_idx)

        imp_options = ["IS", "IR"]
        curr_imp = draft.get("regime_imposition", "IS")
        imp_idx = imp_options.index(curr_imp) if curr_imp in imp_options else 0
        draft["regime_imposition"] = st.radio("Régime d'imposition des bénéfices :", imp_options, index=imp_idx, horizontal=True)

    with col_f2:
        tva_options = [
            "Réel normal (20%)",
            "Réel simplifié",
            "Franchise en base de TVA (art. 293 B du CGI - exonéré)"
        ]
        curr_tva = draft.get("regime_tva", "Réel normal (20%)")
        tva_idx = tva_options.index(curr_tva) if curr_tva in tva_options else 0
        draft["regime_tva"] = st.selectbox("Régime de TVA :", tva_options, index=tva_idx)

        fiscal_dates = ["31/12", "30/06", "30/09", "31/03"]
        curr_fye = draft.get("fiscal_year_end", "31/12")
        fye_idx = fiscal_dates.index(curr_fye) if curr_fye in fiscal_dates else 0
        draft["fiscal_year_end"] = st.selectbox("Date de clôture comptable :", fiscal_dates, index=fye_idx)

    st.write("")

    # --- ÉTAPE 3 : MANDATAIRE & COORDONNÉES DE FACTURATION ---
    st.markdown("### **3. Représentant & Facturation**")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        draft["president"] = st.text_input("Nom du représentant légal :", value=draft.get("president", user_fullname))
        roles = ["Président", "Directeur Général", "Gérant", "Entrepreneur individuel", "Associé gérant", "Titulaire"]
        curr_role = draft.get("president_role", "Dirigeant")
        role_idx = roles.index(curr_role) if curr_role in roles else 0
        draft["president_role"] = st.selectbox("Qualité / Fonction :", roles, index=role_idx)

    with col_d2:
        draft["iban"] = st.text_input("IBAN de facturation (optionnel) :", value=draft.get("iban", ""), placeholder="Ex: FR76 3000 6000 0112 3456 7890 189")
        draft["bic"] = st.text_input("Code BIC (optionnel) :", value=draft.get("bic", ""), placeholder="Ex: BNPAFRPPXXX")

    st.write("")

    col_sub_l, col_sub_btn, col_sub_r = st.columns([1, 2, 1])
    with col_sub_btn:
        btn_label = "Enregistrer cette structure" if user_entities else "Activer mon assistant ÉCHAP"
        if st.button(btn_label, type="primary", use_container_width=True):
            ent_name_val = draft.get("name", "").strip() or f"{user_fullname} ({draft.get('legal_form')})"
            draft["name"] = ent_name_val
            draft["company_name"] = ent_name_val
            draft["representative_name"] = draft.get("president", user_fullname)
            draft["representative_role"] = draft.get("president_role", "Dirigeant")

            res = create_entity_for_user(user_id, draft, role="owner")
            if "error" in res:
                st.error(res["error"])
            else:
                st.session_state.active_entity_id = res["id"]
                st.session_state.adding_entity = False
                st.session_state.pop("ob_draft", None)
                st.session_state.pop("ob_results", None)
                st.success(f"Structure « {ent_name_val} » enregistrée avec succès !")
                st.rerun()

    if is_adding_entity:
        col_c1, col_c2 = st.columns([5, 1])
        with col_c2:
            if st.button("Annuler", type="secondary"):
                st.session_state.adding_entity = False
                st.session_state.pop("ob_draft", None)
                st.rerun()
    else:
        col_dec_l, col_dec_r = st.columns([5, 1])
        with col_dec_r:
            if st.button("Déconnexion", type="secondary"):
                st.session_state.user = None
                st.session_state.pop("ob_draft", None)
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
            all_tvas = ["Réel normal (20%)", "Réel simplifié", "Franchise en base de TVA (art. 293 B du CGI - exonéré)"]
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
