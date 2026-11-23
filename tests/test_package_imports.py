"""
Régression : les imports internes doivent survivre au rechargeur Streamlit.

Le rechargeur de modules de Streamlit retire des entrées de ``sys.modules``
lorsqu'un fichier change. Avec des paquets-espaces de noms (PEP 420), retirer
``packages`` en laissant ses sous-modules provoque ``KeyError: 'packages'``
au prochain import (observé sur Streamlit Cloud / Python 3.14). Les fichiers
``__init__.py`` rendent ``packages`` et ``packages.paperasse`` ordinaires.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestPackageImports(unittest.TestCase):
    """Vérifie la robustesse des paquets face à l'éviction de modules."""

    def test_import_survives_parent_eviction(self):
        """L'import d'``agent`` reste possible après éviction de ``packages``."""
        code = (
            "import sys, importlib\n"
            "import packages.paperasse.auth_db\n"
            "sys.modules.pop('packages', None)\n"
            "importlib.import_module('packages.paperasse.agent')\n"
            "print('OK')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)

    def test_internal_packages_are_regular(self):
        """``packages`` et ``packages.paperasse`` sont des paquets ordinaires."""
        self.assertTrue((ROOT / "packages" / "__init__.py").is_file())
        self.assertTrue((ROOT / "packages" / "paperasse" / "__init__.py").is_file())


if __name__ == "__main__":
    unittest.main()
