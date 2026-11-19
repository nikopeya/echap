"""
Tests unitaires pour l'application ÉCHAP épurée et le pilotage financier.
"""

import unittest
from packages.paperasse.agent import (
    build_unified_system_prompt,
    detect_domain,
    simulate_offline_response,
    DEFAULT_MODEL
)
from packages.paperasse.sources_publiques import (
    search_pcg,
    calculate_ik,
    search_companies
)
from packages.paperasse.auth_db import (
    register_user,
    authenticate_user,
    get_company_finances,
    save_document,
    list_user_documents
)


class TestEchapApp(unittest.TestCase):
    """Vérification de l'interface épurée et des fonctions métier."""

    def test_domain_detection(self):
        """Vérifie le routage automatique et invisible pour l'utilisateur."""
        self.assertEqual(detect_domain("Comment comptabiliser une facture avec TVA ?"), "comptable")
        self.assertEqual(detect_domain("Quel est le barème de l'impôt sur le revenu IR ?"), "fiscaliste")
        self.assertEqual(detect_domain("Comment rédiger les statuts d'une SCI ?"), "notaire")
        self.assertEqual(detect_domain("Que risque-t-on en cas de contrôle fiscal DGFiP ?"), "controleur-fiscal")
        self.assertEqual(detect_domain("Quelle majorité pour l'AG de copropriété ?"), "syndic")

    def test_unified_system_prompt(self):
        """Vérifie la construction du prompt unifié sans mention de Paperasse."""
        prompt = build_unified_system_prompt("ACME SAS", "Question TVA facture")
        self.assertIn("ÉCHAP", prompt)
        self.assertIn("ACME SAS", prompt)
        self.assertNotIn("paperasse", prompt.lower())

    def test_financial_metrics(self):
        """Vérifie la présence et le calcul des indicateurs financiers en temps réel."""
        user = authenticate_user("testeur1", "test1234")
        self.assertIsNotNone(user)
        finances = get_company_finances(user["id"])
        self.assertIn("ca_ytd", finances)
        self.assertIn("tresorerie", finances)
        self.assertIn("creances_clients", finances)
        self.assertIn("tva_due", finances)
        self.assertIn("recent_transactions", finances)
        self.assertIn("echeances", finances)
        self.assertTrue(len(finances["recent_transactions"]) > 0)
        self.assertTrue(len(finances["echeances"]) > 0)

    def test_default_model(self):
        """Vérifie que le modèle par défaut est rapide et économique."""
        self.assertTrue(
            "gemini" in DEFAULT_MODEL or "mistral" in DEFAULT_MODEL or "deepseek" in DEFAULT_MODEL,
            f"Modèle retenu : {DEFAULT_MODEL}"
        )


if __name__ == "__main__":
    unittest.main()
