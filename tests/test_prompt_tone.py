import unittest
import re
from packages.paperasse.agent import build_unified_system_prompt, clean_domain_instructions, load_domain_prompt


class TestPromptTone(unittest.TestCase):
    """Vérifie le respect strict de la charte ÉCHAP : zéro emoji, zéro barre pseudo-graphique, zéro fuite de fichiers internes."""

    def test_no_emojis_in_unified_prompts(self):
        domains_queries = [
            ("ACME Solutions SAS", "salut"),
            ("ACME Solutions SAS", "Facture pour Vitalis"),
            ("SCI Patrimoine", "Statuts et apport immobilier"),
            ("Copropriété Les Pins", "Appel de fonds trimestre"),
            ("Martin Conseil", "Déclaration IR 2042")
        ]
        emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]')
        for comp, query in domains_queries:
            prompt = build_unified_system_prompt(comp, query)
            emojis = emoji_pattern.findall(prompt)
            self.assertEqual(len(emojis), 0, f"Des emojis ont été trouvés dans le prompt ({query}) : {emojis}")

    def test_no_heavy_unicode_separators(self):
        prompt = build_unified_system_prompt("ACME Solutions SAS", "salut")
        self.assertNotIn("━", prompt)
        self.assertNotIn("═", prompt)

    def test_no_internal_file_references_leak(self):
        prompt = build_unified_system_prompt("ACME Solutions SAS", "salut")
        for bad in ["setup-facturation", "references/", "company.json"]:
            self.assertNotIn(bad, prompt, f"Fuite de référence technique interne : {bad}")

    def test_greeting_rule_present(self):
        prompt = build_unified_system_prompt("ACME Solutions SAS", "salut")
        self.assertIn("SALUTATIONS ET OUVERTURE", prompt)
        self.assertIn("ZÉRO EMOJI", prompt)
        self.assertIn("AUCUN SÉPARATEUR PSEUDO-ASCII", prompt)


if __name__ == "__main__":
    unittest.main()
