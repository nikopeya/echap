"""
Tests unitaires pour le module de marque dynamique (Brand & White-Label).
Vérifie la liaison dynamique entre assets/brand/brand.json et le code applicatif.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from packages.paperasse.brand import (
    get_brand,
    get_brand_css,
    get_logo_svg,
    load_brand_config,
    render_brand_login_header,
    render_brand_sidebar_header,
    set_white_label,
)


class TestBrandDynamic(unittest.TestCase):

    def setUp(self):
        # Réinitialise toute surcharge de marque blanche avant chaque test
        set_white_label(None)

    def tearDown(self):
        set_white_label(None)

    def test_load_default_brand(self):
        """Vérifie le chargement de la configuration officielle ECHAP."""
        brand = get_brand()
        self.assertEqual(brand["id"], "echap")
        self.assertEqual(brand["name"], "ECHAP")
        self.assertEqual(brand["tagline"], "Libérez-vous.")
        self.assertIn("paperasse", brand["baseline"])

        # Vérification des couleurs maîtresses
        colors = brand["colors"]
        self.assertEqual(colors["primary"], "#09090B")
        self.assertEqual(colors["secondary"], "#FFFFFF")
        self.assertEqual(colors["accent"], "#EA580C")

    def test_brand_css_generation(self):
        """Vérifie que le CSS généré contient les variables de marque et les couleurs choisies."""
        css = get_brand_css()
        self.assertIn(":root", css)
        self.assertIn("#09090B", css)  # Noir Space Black
        self.assertIn("#EA580C", css)  # Orange Ambre Solaire
        self.assertIn(".metric-card", css)
        self.assertIn(".badge-brand-accent", css)

    def test_logo_svg_loading(self):
        """Vérifie le chargement des logos vectoriels SVG."""
        horizontal_svg = get_logo_svg("horizontal", height=42)
        self.assertIn("<svg", horizontal_svg)
        self.assertIn("height: 42px", horizontal_svg)

        symbol_svg = get_logo_svg("symbol", height=64)
        self.assertIn("<svg", symbol_svg)
        self.assertIn("height: 64px", symbol_svg)

        dark_svg = get_logo_svg("dark", height=32)
        self.assertIn("<svg", dark_svg)

    def test_render_headers(self):
        """Vérifie la génération des blocs HTML pour l'application."""
        login_header = render_brand_login_header()
        self.assertIn("<svg", login_header)
        self.assertIn("Libérez-vous.", login_header)

        sidebar_header = render_brand_sidebar_header("Entreprise Test")
        self.assertIn("<svg", sidebar_header)
        self.assertIn("Entreprise Test", sidebar_header)

    def test_white_label_override(self):
        """Vérifie le basculement dynamique en marque blanche sans modifier le code."""
        white_label_brand = {
            "id": "cabinet_xyz",
            "name": "CABINET XYZ",
            "tagline": "Votre compta simplifiée.",
            "baseline": "La solution sur-mesure de votre expert.",
            "colors": {
                "primary": "#1E293B",
                "primary_surface": "#334155",
                "secondary": "#FFFFFF",
                "accent": "#0D9488",  # Teal personnalisé
                "accent_hover": "#0F766E",
                "accent_light": "#CCFBF1",
                "bg_page": "#F8FAFC",
                "bg_card": "#FFFFFF",
                "border": "#E2E8F0",
                "text_main": "#1E293B",
                "text_secondary": "#64748B",
            },
            "assets": {},
        }

        # Activation marque blanche
        set_white_label(white_label_brand)
        active_brand = get_brand()
        self.assertEqual(active_brand["name"], "CABINET XYZ")
        self.assertEqual(active_brand["tagline"], "Votre compta simplifiée.")

        # Le CSS généré reflète instantanément la nouvelle couleur d'accent Teal
        css = get_brand_css()
        self.assertIn("#0D9488", css)
        self.assertIn("#1E293B", css)

        # Réinitialisation
        set_white_label(None)
        restored_brand = get_brand()
        self.assertEqual(restored_brand["name"], "ECHAP")
        self.assertEqual(restored_brand["colors"]["accent"], "#EA580C")


if __name__ == "__main__":
    unittest.main()
