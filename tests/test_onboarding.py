"""
Tests du parcours d'Onboarding d'ÉCHAP (PAR-01).
Vérifie la qualification d'un nouveau compte entreprise, l'initialisation des échéances,
la persistance du profil, la dissociation utilisateur/structure et le multi-entités.
"""

import sqlite3
import unittest
from packages.paperasse.auth_db import (
    register_user,
    authenticate_user,
    is_onboarding_completed,
    complete_onboarding,
    get_user_entities,
    get_entity_profile,
    create_entity_for_user,
    update_entity_profile,
    get_company_profile,
    get_company_finances,
    load_user_chat,
    seed_default_testers
)
from packages.paperasse.agent import build_unified_system_prompt


class TestOnboarding(unittest.TestCase):

    def test_seed_testers_have_completed_onboarding(self):
        """Les 3 comptes de démo par défaut doivent être pré-qualifiés."""
        seed_default_testers()
        for uid in [1, 2, 3]:
            self.assertTrue(is_onboarding_completed(uid), f"User {uid} devrait être qualifié")
            prof = get_company_profile(uid)
            self.assertNotEqual(prof["siren"], "")
            self.assertNotEqual(prof["president"], "")

    def test_new_user_onboarding_flow(self):
        """Un nouvel utilisateur doit passer par l'onboarding avant d'accéder au service."""
        # 1. Inscription en tant que personne physique sans imposer de nom d'entreprise
        username = "test_onboard_user_1"
        user_res = register_user(username, "secure_pwd_123", full_name="Jean Dupont")
        self.assertIn("id", user_res)
        uid = user_res["id"]

        try:
            # 2. Avant onboarding : non qualifié
            self.assertFalse(is_onboarding_completed(uid))

            # 3. Réalisation de l'onboarding d'une première société
            profile_input = {
                "name": "Ma Super Boite SAS",
                "company_name": "Ma Super Boite SAS",
                "structure_type": "company",
                "legal_form": "SAS",
                "siren": "952981363",
                "siret": "95298136300015",
                "address": "16 Boulevard du Parc",
                "postal_code": "92200",
                "city": "Neuilly-sur-Seine",
                "activity_code": "62.01Z",
                "activity_label": "Édition de logiciels applicatifs",
                "regime_tva": "Réel normal (20%)",
                "regime_imposition": "IS",
                "fiscal_year_end": "31/12",
                "president": "Jean Dupont",
                "president_role": "Président",
                "iban": "FR7630006000011234567890189",
                "bic": "BNPAFRPPXXX"
            }

            res = complete_onboarding(uid, profile_input)
            self.assertTrue(res.get("success"))

            # 4. Après onboarding : qualifié
            self.assertTrue(is_onboarding_completed(uid))

            # 5. Vérification du profil persistant
            prof = get_company_profile(uid)
            self.assertEqual(prof["legal_form"], "SAS")
            self.assertEqual(prof["siren"], "952981363")
            self.assertEqual(prof["president"], "Jean Dupont")
            self.assertEqual(prof["president_role"], "Président")
            self.assertEqual(prof["regime_tva"], "Réel normal (20%)")
            self.assertEqual(prof["fiscal_year_end"], "31/12")
            self.assertEqual(prof["iban"], "FR7630006000011234567890189")

            # 6. Échéances initialisées automatiquement
            finances = get_company_finances(uid)
            labels = [e["label"] for e in finances["echeances"]]
            self.assertTrue(any("TVA" in l for l in labels), "L'échéance TVA doit être créée pour le réel normal")
            self.assertTrue(any("CFE" in l for l in labels), "L'échéance CFE doit être présente")
            self.assertTrue(any("Clôture" in l or "Liasse" in l for l in labels), "L'échéance de liasse fiscale doit être présente")

            # 7. Message d'accueil de l'agent dans le chat
            chat = load_user_chat(uid)
            self.assertGreaterEqual(len(chat), 1)
            welcome_content = chat[0]["content"]
            self.assertIn("Jean Dupont", welcome_content)
            self.assertIn("Ma Super Boite SAS", welcome_content)
            self.assertIn("952981363", welcome_content)

            # 8. Adaptation du prompt système de l'agent
            system_prompt = build_unified_system_prompt("Ma Super Boite SAS", "Génère une facture", prof)
            self.assertIn("Jean Dupont (Président)", system_prompt)
            self.assertIn("FR7630006000011234567890189", system_prompt)
            self.assertIn("952981363", system_prompt)
            self.assertIn("RÉGIME TVA ASSUJETTI", system_prompt)

        finally:
            # Nettoyage
            conn = sqlite3.connect("packages/paperasse/data/echap_mtp.sqlite")
            with conn:
                conn.execute("DELETE FROM users WHERE id = ?", (uid,))

    def test_micro_entreprise_franchise_tva_sans_nom_societe(self):
        """Vérifie l'onboarding d'un auto-entrepreneur sans nom de société imposé."""
        username = "test_onboard_micro_auto"
        # Inscription pure de la personne physique
        user_res = register_user(username, "pwd1234", full_name="Sophie Martin")
        self.assertIn("id", user_res)
        uid = user_res["id"]

        try:
            # Création de la micro-entreprise : aucun nom de société n'est fourni
            profile_input = {
                "name": "",  # Pas de nom de société !
                "structure_type": "micro_enterprise",
                "legal_form": "Micro-entreprise",
                "siren": "777888999",
                "siret": "77788899900012",
                "address": "40 rue de la République",
                "postal_code": "69002",
                "city": "Lyon",
                "activity_code": "70.22Z",
                "activity_label": "Conseil en gestion",
                "regime_tva": "Franchise en base de TVA (art. 293 B du CGI - sans TVA)",
                "regime_imposition": "IR",
                "fiscal_year_end": "31/12",
                "president": "Sophie Martin",
                "president_role": "Entrepreneur individuel",
                "iban": "FR7610058000019876543210145",
                "bic": "SGFRFRPPXXX"
            }

            res = complete_onboarding(uid, profile_input)
            self.assertTrue(res.get("success"))

            prof = get_company_profile(uid)
            # La dénomination a été automatiquement dérivée du nom de la personne physique
            self.assertIn("Sophie Martin", prof.get("name") or prof.get("company_name"))
            self.assertEqual(prof["legal_form"], "Micro-entreprise")

            finances = get_company_finances(uid)
            labels = [e["label"] for e in finances["echeances"]]

            # Échéance URSSAF et statut Franchise
            self.assertTrue(any("URSSAF" in l for l in labels))
            self.assertTrue(any("Franchise" in l for l in labels))

            # Directive TVA dans le prompt de l'agent
            system_prompt = build_unified_system_prompt("Sophie Martin EI", "Peux-tu faire un devis ?", prof)
            self.assertIn("FRANCHISE EN BASE - ART. 293 B CGI", system_prompt)
            self.assertIn("TVA non applicable, article 293 B du Code Général des Impôts", system_prompt)

        finally:
            conn = sqlite3.connect("packages/paperasse/data/echap_mtp.sqlite")
            with conn:
                conn.execute("DELETE FROM users WHERE id = ?", (uid,))

    def test_multi_entities_for_single_user(self):
        """Vérifie qu'un même utilisateur peut piloter 1 Micro-entreprise + 1 SAS + 1 SCI distinctes."""
        username = "serial_entrepreneur"
        u = register_user(username, "multi_pass_99", full_name="Nicolas Entrepreneur")
        uid = u["id"]

        try:
            # 1. Structure 1 : Micro-entreprise de freelance
            e1 = create_entity_for_user(uid, {
                "structure_type": "micro_enterprise",
                "legal_form": "Micro-entreprise",
                "representative_name": "Nicolas Entrepreneur",
                "representative_role": "Entrepreneur individuel",
                "regime_tva": "Franchise en base de TVA (art. 293 B)",
                "regime_imposition": "IR"
            })
            self.assertTrue(e1.get("success"))

            # 2. Structure 2 : SAS commerciale
            e2 = create_entity_for_user(uid, {
                "name": "TechStudio SAS",
                "structure_type": "company",
                "legal_form": "SAS",
                "representative_name": "Nicolas Entrepreneur",
                "representative_role": "Président",
                "siren": "952111222",
                "regime_tva": "Réel normal (20%)",
                "regime_imposition": "IS"
            })
            self.assertTrue(e2.get("success"))

            # 3. Structure 3 : SCI de patrimoine
            e3 = create_entity_for_user(uid, {
                "name": "SCI Patrimoine Familial",
                "structure_type": "sci",
                "legal_form": "SCI",
                "representative_name": "Nicolas Entrepreneur",
                "representative_role": "Gérant",
                "siren": "888999000",
                "regime_imposition": "IS"
            })
            self.assertTrue(e3.get("success"))

            # Vérification : l'utilisateur a bien 3 entités distinctes
            ents = get_user_entities(uid)
            self.assertEqual(len(ents), 3)
            types = [e["structure_type"] for e in ents]
            self.assertIn("micro_enterprise", types)
            self.assertIn("company", types)
            self.assertIn("sci", types)

            # Vérification de l'isolation des données par entité
            prof_micro = get_entity_profile(e1["id"])
            prof_sas = get_entity_profile(e2["id"])
            prof_sci = get_entity_profile(e3["id"])

            self.assertEqual(prof_micro["legal_form"], "Micro-entreprise")
            self.assertEqual(prof_sas["legal_form"], "SAS")
            self.assertEqual(prof_sci["legal_form"], "SCI")

            # Finances isolées
            fin_micro = get_company_finances(uid, entity_id=e1["id"])
            fin_sas = get_company_finances(uid, entity_id=e2["id"])
            self.assertTrue(any("URSSAF" in ech["label"] for ech in fin_micro["echeances"]))
            self.assertTrue(any("TVA" in ech["label"] for ech in fin_sas["echeances"]))

        finally:
            conn = sqlite3.connect("packages/paperasse/data/echap_mtp.sqlite")
            with conn:
                conn.execute("DELETE FROM users WHERE id = ?", (uid,))
                conn.execute("DELETE FROM memberships WHERE user_id = ?", (uid,))


if __name__ == "__main__":
    unittest.main()
