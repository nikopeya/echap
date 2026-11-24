"""
Tests des règles du formulaire d'onboarding (cohérence des questions).

Les fonctions testées sont pures : elles ne dépendent ni de Streamlit ni de
la base de données. Elles garantissent que les choix proposés correspondent
au type de structure sélectionné.
"""

import unittest

from packages.paperasse.agent import build_unified_system_prompt
from packages.paperasse.onboarding import (
    TVA_EXONERATION_261D,
    TVA_FRANCHISE,
    TVA_NORMAL,
    apply_company_to_draft,
    company_suggestion_label,
    legal_form_from_company,
    missing_identity_fields,
    role_options,
    select_structure,
    structure_defaults,
    tva_choices,
)


class TestOnboardingRules(unittest.TestCase):

    def test_structure_defaults_are_coherent(self):
        company = structure_defaults("company")
        self.assertEqual(company["legal_form"], "SAS")
        self.assertEqual(company["regime_tva"], TVA_NORMAL)
        self.assertEqual(company["regime_imposition"], "IS")
        self.assertEqual(company["president_role"], "Président")

        micro = structure_defaults("micro_enterprise")
        self.assertEqual(micro["legal_form"], "Micro-entreprise")
        self.assertEqual(micro["regime_tva"], TVA_FRANCHISE)
        self.assertEqual(micro["regime_imposition"], "IR")

        sci = structure_defaults("sci")
        self.assertEqual(sci["legal_form"], "SCI")
        self.assertEqual(sci["regime_tva"], TVA_EXONERATION_261D)
        self.assertEqual(sci["regime_imposition"], "IR")
        self.assertEqual(sci["president_role"], "Gérant")

        liberal = structure_defaults("liberal")
        self.assertEqual(liberal["legal_form"], "Profession libérale (BNC)")
        self.assertEqual(liberal["regime_imposition"], "IR")
        self.assertEqual(liberal["president_role"], "Titulaire libéral")

    def test_select_structure_resets_stale_identity(self):
        draft = {
            "structure_type": "micro_enterprise",
            "name": "Sophie Martin EI",
            "address": "1 rue de Test",
            "city": "Lyon",
        }
        select_structure(draft, "company", "Sophie Martin")
        self.assertEqual(draft["name"], "")
        self.assertEqual(draft["address"], "")
        self.assertEqual(draft["legal_form"], "SAS")
        self.assertEqual(draft["regime_tva"], TVA_NORMAL)

        select_structure(draft, "micro_enterprise", "Sophie Martin")
        self.assertEqual(draft["name"], "Sophie Martin EI")
        self.assertEqual(draft["regime_tva"], TVA_FRANCHISE)

    def test_legal_form_mapping_from_api_codes_and_labels(self):
        self.assertEqual(
            legal_form_from_company({"nature_juridique": "5710", "nom_complet": "DOCTOLIB"}),
            "SAS",
        )
        self.assertEqual(
            legal_form_from_company({"nature_juridique": "5499", "nom_complet": "MA SARL"}),
            "SARL",
        )
        self.assertEqual(
            legal_form_from_company({"nature_juridique": "5499", "nom_complet": "EURL TEST"}),
            "EURL",
        )
        self.assertEqual(
            legal_form_from_company({"nature_juridique": "5710", "nom_complet": "MA BOITE SASU"}),
            "SASU",
        )
        self.assertEqual(
            legal_form_from_company(
                {"nature_juridique": "Société civile immobilière", "nom_complet": "PIERRE & PATRIMOINE"}
            ),
            "SCI",
        )
        self.assertEqual(
            legal_form_from_company({"nature_juridique": "1000", "nom_complet": "JEAN DUPONT"}),
            "Micro-entreprise",
        )
        self.assertEqual(
            legal_form_from_company({"nature_juridique": "", "nom_complet": "SCIENTIFIQUE SAS"}),
            "SAS",
        )

    def test_apply_company_to_draft_fills_registry_data(self):
        draft = select_structure({}, "company", "Nicolas Entrepreneur")
        company = {
            "nom_complet": "TECH STUDIO SARL",
            "siren": "952111222",
            "siret": "95211122200015",
            "nature_juridique": "5499",
            "adresse": "12 rue de la Paix",
            "code_postal": "75002",
            "ville": "PARIS",
            "activite_principale": "62.01Z",
            "libelle_activite": "Édition de logiciels",
            "dirigeants": [
                {"nom": "MARTIN", "prenoms": "Claire", "qualite": "Gérante", "type_dirigeant": "personne physique"}
            ],
        }
        apply_company_to_draft(draft, company, "Nicolas Entrepreneur")

        self.assertEqual(draft["name"], "TECH STUDIO SARL")
        self.assertEqual(draft["legal_form"], "SARL")
        self.assertEqual(draft["structure_type"], "company")
        self.assertEqual(draft["address"], "12 rue de la Paix")
        self.assertEqual(draft["postal_code"], "75002")
        self.assertEqual(draft["city"], "PARIS")
        self.assertEqual(draft["siren"], "952111222")
        self.assertEqual(draft["president"], "Claire MARTIN")
        self.assertEqual(draft["president_role"], "Gérant")

    def test_registry_address_does_not_duplicate_postal_code(self):
        draft = select_structure({}, "company", "Nicolas Entrepreneur")
        company = {
            "nom_complet": "DOCTOLIB",
            "nature_juridique": "5710",
            "adresse": "54 QUAI CHARLES PASQUA 92300 LEVALLOIS-PERRET",
            "code_postal": "92300",
            "ville": "LEVALLOIS-PERRET",
        }
        apply_company_to_draft(draft, company, "Nicolas Entrepreneur")
        self.assertEqual(draft["address"], "54 QUAI CHARLES PASQUA")
        self.assertEqual(draft["postal_code"], "92300")
        self.assertEqual(draft["city"], "LEVALLOIS-PERRET")

    def test_sci_search_switches_structure_and_tva(self):
        draft = select_structure({}, "company", "Claire Martin")
        company = {
            "nom_complet": "SCI PIERRE & PATRIMOINE",
            "siren": "850987654",
            "siret": "85098765400012",
            "nature_juridique": "Société civile immobilière",
            "adresse": "45 avenue Victor Hugo",
            "code_postal": "69002",
            "ville": "LYON",
            "dirigeants": [
                {"nom": "MARTIN", "prenoms": "Claire", "qualite": "Gérante", "type_dirigeant": "personne physique"}
            ],
        }
        apply_company_to_draft(draft, company, "Claire Martin")

        self.assertEqual(draft["structure_type"], "sci")
        self.assertEqual(draft["legal_form"], "SCI")
        self.assertEqual(draft["regime_tva"], TVA_EXONERATION_261D)
        self.assertEqual(draft["regime_imposition"], "IR")
        self.assertEqual(draft["president_role"], "Gérant")

    def test_tva_question_is_adapted_to_structure(self):
        company_choices = tva_choices("company")
        self.assertEqual(company_choices[0]["value"], TVA_NORMAL)
        self.assertIn("société", company_choices[-1]["description"].lower())
        self.assertNotEqual(company_choices[0]["value"], TVA_FRANCHISE)

        sci_choices = tva_choices("sci")
        self.assertEqual(sci_choices[0]["value"], TVA_EXONERATION_261D)
        self.assertIn("261", sci_choices[0]["description"])

        micro_choices = tva_choices("micro_enterprise")
        self.assertEqual(micro_choices[0]["value"], TVA_FRANCHISE)
        self.assertEqual(len({c["value"] for c in micro_choices}), 3)

    def test_roles_keep_atypical_current_role(self):
        roles = role_options("Titulaire libéral")
        self.assertIn("Titulaire libéral", roles)
        self.assertIn("Président", roles)

    def test_missing_identity_fields(self):
        self.assertEqual(
            missing_identity_fields({}),
            ["le nom de la structure", "l'adresse", "le code postal", "la ville"],
        )
        self.assertEqual(
            missing_identity_fields(
                {"name": "Ma SAS", "address": "1 rue", "postal_code": "75001", "city": "Paris"}
            ),
            [],
        )

    def test_suggestion_label_contains_siren_and_city(self):
        label = company_suggestion_label(
            {"nom_complet": "ACME CONSEIL", "siren": "900123456", "ville": "PARIS"}
        )
        self.assertIn("ACME CONSEIL", label)
        self.assertIn("900123456", label)
        self.assertIn("PARIS", label)

    def test_sci_prompt_uses_261d_mention(self):
        profile = {
            "legal_form": "SCI",
            "regime_tva": TVA_EXONERATION_261D,
            "regime_imposition": "IR",
            "president": "Claire Martin",
            "president_role": "Gérant",
        }
        prompt = build_unified_system_prompt("SCI Pierre & Patrimoine", "Prépare une quittance", profile)
        self.assertIn("ART. 261 D CGI", prompt)
        self.assertIn("article 261 D du Code Général des Impôts", prompt)
        self.assertNotIn("article 293 B du Code Général des Impôts", prompt)


if __name__ == "__main__":
    unittest.main()
