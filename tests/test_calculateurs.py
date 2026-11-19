"""
Tests unitaires pour les calculateurs déterministes et analyseurs de Paperasse.
"""

import unittest
from packages.paperasse.calculateurs import (
    calculer_is,
    calculer_amortissement,
    calculer_acomptes_tva,
    calculer_impot_revenu,
    analyser_fec_content
)


class TestCalculateurs(unittest.TestCase):
    """Vérification des calculs fiscaux et comptables déterministes."""

    def test_calcul_is_pme(self):
        """Vérifie le calcul de l'IS à 15% et 25% (CGI art. 219)."""
        # Bénéfice de 50 000 € : 42 500 € à 15% (6 375 €) + 7 500 € à 25% (1 875 €) = 8 250 €
        res = calculer_is(50000.0)
        self.assertEqual(res["total_is_du"], 8250.0)
        self.assertEqual(res["impot_15_pct"], 6375.0)
        self.assertEqual(res["impot_25_pct"], 1875.0)
        self.assertEqual(res["economie_taux_reduit_pme"], 4250.0)
        self.assertEqual(len(res["acomptes_trimestriels"]), 4)

    def test_amortissement_lineaire(self):
        """Vérifie le tableau d'amortissement avec prorata temporis."""
        # Bien de 3 000 € sur 3 ans, mis en service en juin (7 mois première année)
        res = calculer_amortissement(3000.0, 3, mois_mise_en_service=6)
        self.assertEqual(res["valeur_brute_ht"], 3000.0)
        self.assertEqual(res["taux_lineaire_pct"], 33.33)
        tableau = res["tableau_amortissement"]
        # Annuité 1 : 1000 * 7/12 = 583.33 €
        self.assertEqual(tableau[0]["dotation"], 583.33)
        # Total amorti = 3000 €
        total_amorti = sum(t["dotation"] for t in tableau)
        self.assertAlmostEqual(total_amorti, 3000.0, places=1)

    def test_acomptes_tva(self):
        """Vérifie les acomptes semestriels de TVA au régime réel simplifié (55% et 40%)."""
        res = calculer_acomptes_tva(10000.0)
        self.assertFalse(res["dispense_acomptes"])
        self.assertEqual(res["acompte_juillet"], 5500.0)
        self.assertEqual(res["acompte_decembre"], 4000.0)

        # Dispense si TVA < 1 000 €
        res_disp = calculer_acomptes_tva(800.0)
        self.assertTrue(res_disp["dispense_acomptes"])

    def test_impot_revenu_2026(self):
        """Vérifie le barème progressif de l'IR 2026."""
        # Célibataire 45 000 € net imposable
        res = calculer_impot_revenu(45000.0, nb_parts=1.0)
        self.assertEqual(res["taux_marginal_imposition_pct"], 30)
        self.assertTrue(res["impot_net_a_payer"] > 0)


if __name__ == "__main__":
    unittest.main()
