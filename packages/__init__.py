"""Paquet racine des composants ÉCHAP réemployés.

Fichier volontairement présent pour que ``packages`` soit un paquet Python
ordinaire et non un paquet-espace de noms (PEP 420). Sans cela, le rechargeur
de modules de Streamlit peut retirer ``packages`` de ``sys.modules`` en
laissant ses sous-modules : leur chemin d'espace de noms lève alors
``KeyError: 'packages'`` au prochain import.
"""
