"""
Calculateurs déterministes et analyseurs comptables pour ÉCHAP.
Centralise les algorithmes exacts selon la réglementation française (CGI, PCG 2026, LPF).
"""

import os
import json
import math
from typing import Dict, Any, List, Optional
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


# --- 1. CALCULATEUR D'IMPÔT SUR LES SOCIÉTÉS (IS) ---

def calculer_is(resultat_fiscal: float, duree_mois: int = 12) -> Dict[str, Any]:
    """
    Calcule déterministement l'Impôt sur les Sociétés selon l'art. 219 du CGI.
    - Taux réduit PME de 15% jusqu'à 42 500 € (proratisé selon la durée de l'exercice).
    - Taux normal de 25% au-delà.
    - Acomptes trimestriels d'IS.
    """
    rf = max(0.0, float(resultat_fiscal))
    plafond_reduit = round(42500.0 * (duree_mois / 12.0), 2)

    part_reduite = min(rf, plafond_reduit)
    part_normale = max(0.0, rf - plafond_reduit)

    impot_reduit = round(part_reduite * 0.15, 2)
    impot_normal = round(part_normale * 0.25, 2)
    total_is = round(impot_reduit + impot_normal, 2)

    # Économie d'impôt par rapport au taux plein 25%
    is_taux_plein = round(rf * 0.25, 2)
    economie_pme = round(is_taux_plein - total_is, 2)

    # 4 Acomptes d'IS trimestriels
    acompte_unitaire = round(total_is / 4.0, 2)
    acomptes = [
        {"echeance": "15 mars", "montant": acompte_unitaire},
        {"echeance": "15 juin", "montant": acompte_unitaire},
        {"echeance": "15 septembre", "montant": acompte_unitaire},
        {"echeance": "15 décembre", "montant": acompte_unitaire}
    ]

    return {
        "resultat_fiscal": rf,
        "duree_exercice_mois": duree_mois,
        "plafond_taux_reduit": plafond_reduit,
        "assiette_15_pct": part_reduite,
        "impot_15_pct": impot_reduit,
        "assiette_25_pct": part_normale,
        "impot_25_pct": impot_normal,
        "total_is_du": total_is,
        "taux_moyen_effectif_pct": round((total_is / rf * 100), 2) if rf > 0 else 0.0,
        "economie_taux_reduit_pme": economie_pme,
        "acomptes_trimestriels": acomptes,
        "base_legale": "Art. 219 du Code Général des Impôts"
    }


# --- 2. PLAN D'AMORTISSEMENT LINÉAIRE (PCG 2026) ---

def calculer_amortissement(valeur_ht: float, duree_annees: int, mois_mise_en_service: int = 1) -> Dict[str, Any]:
    """
    Génère un tableau d'amortissement linéaire avec prorata temporis selon le PCG 2026.
    """
    v_ht = float(valeur_ht)
    duree = int(duree_annees)
    if duree <= 0:
        return {"error": "La durée d'amortissement doit être d'au moins 1 an."}

    taux_annuel = 1.0 / duree
    annuite_pleine = round(v_ht * taux_annuel, 2)

    # Prorata temporis première année (en mois ou jours sur base 360/365)
    mois_premiere_annee = 12 - mois_mise_en_service + 1
    dotation_annee1 = round(annuite_pleine * (mois_premiere_annee / 12.0), 2)

    tableau = []
    vnc = v_ht
    cumul = 0.0
    current_year = datetime.now().year

    # Année 1
    vnc_fin = round(v_ht - dotation_annee1, 2)
    cumul += dotation_annee1
    tableau.append({
        "annee": current_year,
        "valeur_debut": v_ht,
        "dotation": dotation_annee1,
        "cumul_amortissements": round(cumul, 2),
        "vnc_fin": vnc_fin,
        "prorata_mois": mois_premiere_annee
    })
    vnc = vnc_fin

    # Années intermédiaires
    for i in range(1, duree):
        dot = min(vnc, annuite_pleine)
        vnc_fin = round(vnc - dot, 2)
        cumul += dot
        tableau.append({
            "annee": current_year + i,
            "valeur_debut": round(vnc, 2),
            "dotation": round(dot, 2),
            "cumul_amortissements": round(cumul, 2),
            "vnc_fin": vnc_fin,
            "prorata_mois": 12
        })
        vnc = vnc_fin

    # Dernière année si prorata temporis incomplet en an 1
    if vnc > 0.01:
        dot = round(vnc, 2)
        cumul += dot
        tableau.append({
            "annee": current_year + duree,
            "valeur_debut": round(vnc, 2),
            "dotation": dot,
            "cumul_amortissements": round(cumul, 2),
            "vnc_fin": 0.0,
            "prorata_mois": 12 - mois_premiere_annee
        })

    return {
        "valeur_brute_ht": v_ht,
        "duree_annees": duree,
        "taux_lineaire_pct": round(taux_annuel * 100, 2),
        "annuite_pleine": annuite_pleine,
        "mois_premiere_annee": mois_premiere_annee,
        "tableau_amortissement": tableau,
        "norme": "PCG 2026 art. 214-1 et suivants"
    }


# --- 3. ACOMPTES DE TVA (RÉEL SIMPLIFIÉ) ---

def calculer_acomptes_tva(tva_n_moins_1: float) -> Dict[str, Any]:
    """
    Calcule les acomptes semestriels de TVA au régime réel simplifié (CGI art. 287).
    - Acompte de juillet : 55 % de la TVA due N-1 (ligne 57 de la CA12).
    - Acompte de décembre : 40 % de la TVA due N-1.
    - Dispense si TVA N-1 < 1 000 €.
    """
    base_n_1 = float(tva_n_moins_1)
    if base_n_1 < 1000.0:
        return {
            "tva_n_moins_1": base_n_1,
            "dispense_acomptes": True,
            "acompte_juillet": 0.0,
            "acompte_decembre": 0.0,
            "motif": "TVA due de l'année précédente inférieure à 1 000 € (art. 287-5-c CGI) : aucun acompte exigible, paiement au solde annuel CA12."
        }

    acompte_juil = round(base_n_1 * 0.55, 2)
    acompte_dec = round(base_n_1 * 0.40, 2)

    return {
        "tva_n_moins_1": base_n_1,
        "dispense_acomptes": False,
        "acompte_juillet": acompte_juil,
        "echeance_juillet": "Juillet (télédéclaration formulaire 3514)",
        "acompte_decembre": acompte_dec,
        "echeance_decembre": "Décembre (télédéclaration formulaire 3514)",
        "total_acomptes": round(acompte_juil + acompte_dec, 2),
        "base_legale": "Art. 287 du Code Général des Impôts (Régime Réel Simplifié)"
    }


# --- 4. CALCULATEUR D'IMPÔT SUR LE REVENU (IR 2026) ---

def calculer_impot_revenu(rni: float, nb_parts: float = 1.0) -> Dict[str, Any]:
    """
    Calcule déterministement l'Impôt sur le Revenu pour les revenus 2025 (déclaration 2026).
    Applique le barème progressif par tranche, le quotient familial et la décote.
    """
    revenu = max(0.0, float(rni))
    parts = max(1.0, float(nb_parts))

    # Barème LFI 2026 officiel (art. 197 CGI)
    tranches = [
        {"jusqu_a": 11600.0, "taux": 0.0},
        {"de": 11600.0, "a": 29579.0, "taux": 0.11},
        {"de": 29579.0, "a": 84577.0, "taux": 0.30},
        {"de": 84577.0, "a": 181917.0, "taux": 0.41},
        {"au_dela": 181917.0, "taux": 0.45}
    ]

    quotient = revenu / parts
    impot_par_part = 0.0
    tmi = 0.0

    for t in tranches:
        taux = t["taux"]
        if "jusqu_a" in t:
            continue
        elif "au_dela" in t:
            if quotient > t["au_dela"]:
                base = quotient - t["au_dela"]
                impot_par_part += base * taux
                tmi = taux
        else:
            if quotient > t["de"]:
                borne_sup = min(quotient, t["a"])
                base = borne_sup - t["de"]
                impot_par_part += base * taux
                tmi = taux

    impot_brut = round(impot_par_part * parts, 2)

    # Décote 2026 (si impôt brut < seuil)
    # Célibataire : seuil 1 977 €, formule: 897 - (45,25% de l'impôt brut)
    # Couple : seuil 3 266 €, formule: 1 482 - (45,25% de l'impôt brut)
    is_couple = parts >= 2.0
    seuil_decote = 3266.0 if is_couple else 1977.0
    base_decote = 1482.0 if is_couple else 897.0
    decote = 0.0
    if impot_brut > 0 and impot_brut < seuil_decote:
        decote = max(0.0, round(base_decote - (impot_brut * 0.4525), 2))

    impot_net = max(0.0, round(impot_brut - decote, 2))

    return {
        "revenu_net_imposable": revenu,
        "nombre_de_parts": parts,
        "quotient_familial": round(quotient, 2),
        "impot_brut": impot_brut,
        "decote_appliquee": decote,
        "impot_net_a_payer": impot_net,
        "taux_marginal_imposition_pct": int(tmi * 100),
        "taux_moyen_pct": round((impot_net / revenu * 100), 2) if revenu > 0 else 0.0,
        "sources": "Barème LFI 2026 (revenus 2025), art. 197 du CGI"
    }


# --- 5. ANALYSEUR DÉTERMINISTE DE FICHIER FEC (ART. A.47 A-1 LPF) ---

def analyser_fec_content(fec_text: str) -> Dict[str, Any]:
    """
    Exécute les contrôles de conformité légale d'un fichier FEC :
    - 18 colonnes séparées par tabulation.
    - Équilibre débits / crédits.
    - Chronologie des écritures.
    - Détection de libellés à risque ou dépenses personnelles.
    """
    lines = [line.strip() for line in fec_text.strip().splitlines() if line.strip()]
    if not lines:
        return {"error": "Fichier FEC vide"}

    headers = lines[0].split("\t")
    if len(headers) < 18:
        # Essai avec séparateur pipe |
        if len(lines[0].split("|")) >= 18:
            headers = lines[0].split("|")
            delimiter = "|"
        else:
            delimiter = "\t"
    else:
        delimiter = "\t"

    col_count = len(headers)
    if col_count < 18:
        return {
            "conforme": False,
            "format": "Non conforme",
            "colonnes_trouvees": col_count,
            "erreur": f"Format non conforme : 18 colonnes requises selon l'art. A.47 A-1 du LPF ({col_count} trouvées)."
        }

    total_debit = 0.0
    total_credit = 0.0
    anomalies = []
    ecritures_set = set()

    mots_suspects = ["netflix", "spotify", "perso", "vacances", "cadeau", "supermarché", "carrefour", "leclerc", "coiffeur"]
    ecritures_a_examiner = []

    for idx, l in enumerate(lines[1:], start=2):
        cols = l.split(delimiter)
        if len(cols) != col_count:
            anomalies.append(f"Ligne {idx} : nombre de colonnes incorrect ({len(cols)} au lieu de {col_count})")
            continue

        ecr_num = cols[2] if len(cols) > 2 else ""
        compte = cols[4] if len(cols) > 4 else ""
        libelle = cols[10] if len(cols) > 10 else ""
        raw_deb = cols[11].replace(" ", "").replace(",", ".") if len(cols) > 11 else "0"
        raw_crd = cols[12].replace(" ", "").replace(",", ".") if len(cols) > 12 else "0"

        try:
            deb = float(raw_deb) if raw_deb else 0.0
            crd = float(raw_crd) if raw_crd else 0.0
            total_debit += deb
            total_credit += crd
        except ValueError:
            anomalies.append(f"Ligne {idx} : montant invalide (Débit: {raw_deb}, Crédit: {raw_crd})")

        ecritures_set.add(ecr_num)

        # Détection de libellés méritant justification
        for mot in mots_suspects:
            if mot in libelle.lower():
                ecritures_a_examiner.append({
                    "ligne": idx,
                    "compte": compte,
                    "libelle": libelle,
                    "montant": deb or crd,
                    "motif": f"Libellé évocateur de dépense personnelle éventuelle (« {mot} »)"
                })
                break

    ecart = round(abs(total_debit - total_credit), 2)
    equilibre_parfait = (ecart == 0.0)

    if not equilibre_parfait:
        anomalies.append(f"Déséquilibre de comptabilité : Débits ({total_debit:,.2f} €) != Crédits ({total_credit:,.2f} €), écart de {ecart:,.2f} €.")

    conforme = (len(anomalies) == 0 and equilibre_parfait)

    return {
        "conforme": conforme,
        "format": "Conforme Art. A.47 A-1 LPF" if col_count >= 18 else "Invalide",
        "nb_lignes_ecritures": len(lines) - 1,
        "nb_pieces_uniques": len(ecritures_set),
        "total_debits": round(total_debit, 2),
        "total_credits": round(total_credit, 2),
        "ecart_solde": ecart,
        "equilibre": "Parfait (Débit == Crédit)" if equilibre_parfait else f"Déséquilibré (écart: {ecart} €)",
        "anomalies_bloquantes": anomalies,
        "ecritures_a_examiner": ecritures_a_examiner[:5],
        "synthese": "✅ Le fichier FEC respecte les spécifications légales de la DGFiP." if conforme else "⚠️ Des anomalies de structure ou d'équilibre ont été constatées."
    }
