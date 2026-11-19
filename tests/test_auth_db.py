"""
Tests unitaires pour l'authentification et la persistance des testeurs.
"""

import unittest
from packages.paperasse.auth_db import (
    register_user,
    authenticate_user,
    save_user_message,
    load_user_chat,
    save_document,
    list_user_documents,
    get_document_content
)


class TestAuthDB(unittest.TestCase):
    """Vérification de l'authentification, de l'isolation et de la persistance."""

    def test_default_accounts_exist(self):
        """Vérifie que les comptes par défaut fonctionnent."""
        user = authenticate_user("testeur1", "test1234")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "testeur1")
        self.assertEqual(user["company_name"], "ACME Solutions SAS")

        # Mauvais mot de passe
        bad = authenticate_user("testeur1", "mauvais_mdp")
        self.assertIsNone(bad)

    def test_user_registration(self):
        """Vérifie la création d'un nouvel espace testeur."""
        new_u = register_user("nouveau_testeur", "Ma Nouvelle Entreprise", "secretpass")
        if "error" not in new_u:
            self.assertEqual(new_u["username"], "nouveau_testeur")
            # Connexion avec ce nouveau compte
            auth = authenticate_user("nouveau_testeur", "secretpass")
            self.assertIsNotNone(auth)
            self.assertEqual(auth["company_name"], "Ma Nouvelle Entreprise")

    def test_chat_persistence_and_isolation(self):
        """Vérifie que les messages sont persistés et isolés entre testeurs."""
        u1 = authenticate_user("testeur1", "test1234")
        u2 = authenticate_user("testeur2", "test1234")

        # Testeur 1 envoie un message
        save_user_message(u1["id"], "user", "Message secret testeur 1")
        # Testeur 2 envoie un message
        save_user_message(u2["id"], "user", "Message distinct testeur 2")

        # Vérification des messages de Testeur 1
        msgs1 = load_user_chat(u1["id"])
        self.assertTrue(any("Message secret testeur 1" in m["content"] for m in msgs1))
        self.assertFalse(any("Message distinct testeur 2" in m["content"] for m in msgs1))

        # Vérification des messages de Testeur 2
        msgs2 = load_user_chat(u2["id"])
        self.assertTrue(any("Message distinct testeur 2" in m["content"] for m in msgs2))
        self.assertFalse(any("Message secret testeur 1" in m["content"] for m in msgs2))

    def test_document_persistence_blob(self):
        """Vérifie le stockage binaire BLOB des pièces et leur isolation."""
        u1 = authenticate_user("testeur1", "test1234")
        u2 = authenticate_user("testeur2", "test1234")

        raw_bytes = b"CONTENU_FICHIER_TEST_PERSISTANT"
        save_document(u1["id"], "releve_fictif.csv", raw_bytes, kind="upload")

        # Testeur 1 doit voir son fichier
        docs1 = list_user_documents(u1["id"], kind="upload")
        self.assertTrue(any(d["filename"] == "releve_fictif.csv" for d in docs1))

        # Testeur 2 ne doit pas voir le fichier de Testeur 1
        docs2 = list_user_documents(u2["id"], kind="upload")
        self.assertFalse(any(d["filename"] == "releve_fictif.csv" for d in docs2))

        # Récupération du contenu
        target_doc = [d for d in docs1 if d["filename"] == "releve_fictif.csv"][0]
        fname, content = get_document_content(u1["id"], target_doc["id"])
        self.assertEqual(fname, "releve_fictif.csv")
        self.assertEqual(content, raw_bytes)


if __name__ == "__main__":
    unittest.main()
