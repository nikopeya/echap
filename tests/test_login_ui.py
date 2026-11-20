"""
Tests de l'écran de connexion et d'inscription (parcours réel Streamlit).

Ils garantissent que le bouton « Créer mon compte » crée effectivement le compte
et que les messages d'erreur sont affichés au lieu d'un écran figé.
"""

import random
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from packages.paperasse.auth_db import get_db_connection

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def _unique_username(prefix: str) -> str:
    return f"{prefix}_{random.randint(100000, 999999)}"


class TestLoginUI(unittest.TestCase):
    """Vérification des formulaires de connexion et de création de compte."""

    def _register_account(self, at: AppTest, username: str, password: str, full_name: str = "Test UI"):
        at.radio(key="auth_mode").set_value("Créer un compte").run()
        at.text_input(key="reg_name").set_value(full_name)
        at.text_input(key="reg_user").set_value(username)
        at.text_input(key="reg_pass").set_value(password)
        at.button(key="FormSubmitter:form_register-Créer mon compte").click().run()

    def test_register_creates_account_and_opens_onboarding(self):
        """Le formulaire d'inscription crée le compte et mène à la configuration."""
        at = AppTest.from_file(APP_PATH, default_timeout=60)
        at.run()
        username = _unique_username("uitest")
        self._register_account(at, username, "test1234", "Test Inscription")

        user = at.session_state.get("user")
        self.assertIsNotNone(user, "Le compte doit être créé et la session ouverte.")
        self.assertEqual(user["username"], username)

        onboarding = " ".join(m.value for m in at.markdown)
        self.assertIn("Étape 1 sur 4", onboarding)

    def test_register_rejects_short_password(self):
        """Un mot de passe trop court affiche une erreur explicite."""
        at = AppTest.from_file(APP_PATH, default_timeout=60)
        at.run()
        self._register_account(at, _unique_username("uitest"), "123")

        self.assertIsNone(at.session_state.get("user"))
        errors = [e.value for e in at.error]
        self.assertTrue(any("au moins 6 caractères" in e for e in errors), errors)

    def test_login_with_demo_account(self):
        """Le formulaire de connexion ouvre bien la session du compte démo."""
        at = AppTest.from_file(APP_PATH, default_timeout=60)
        at.run()
        at.text_input(key="login_username").set_value("testeur1")
        at.text_input(key="login_password").set_value("test1234")
        at.button(key="FormSubmitter:form_login-Se connecter").click().run()

        user = at.session_state.get("user")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "testeur1")

    def test_login_wrong_password_shows_error(self):
        """Un mauvais mot de passe affiche une erreur au lieu de ne rien faire."""
        at = AppTest.from_file(APP_PATH, default_timeout=60)
        at.run()
        at.text_input(key="login_username").set_value("testeur1")
        at.text_input(key="login_password").set_value("mauvais_mdp")
        at.button(key="FormSubmitter:form_login-Se connecter").click().run()

        self.assertIsNone(at.session_state.get("user"))
        errors = [e.value for e in at.error]
        self.assertTrue(any("incorrect" in e for e in errors), errors)


class TestSchemaInit(unittest.TestCase):
    """Le schéma ne doit être vérifié qu'une seule fois par processus."""

    def test_schema_ready_after_connection(self):
        import packages.paperasse.auth_db as auth_db

        conn = get_db_connection()
        conn.close()
        self.assertTrue(auth_db._schema_ready)


if __name__ == "__main__":
    unittest.main()
