# ÉCHAP — Registre des décisions

Date d’initialisation : 2026-11-10. Source des arbitrages : discussion de cadrage avec le porteur du projet. Ce registre est la référence des décisions ; la spécification détaille leur application.

## 1. Statuts et évolution

- **Acté** : décision explicite du porteur, non synonyme de livraison.
- **Proposé** : recommandation non encore approuvée.
- **À vérifier** : fait ou faisabilité nécessitant une preuve.
- **Ouvert** : choix à arbitrer.
- **Remplacé** : ancienne décision conservée avec lien vers la nouvelle.

Ne pas transformer une recommandation antérieure de l’assistant en décision utilisateur. En cas de pivot, ajouter une nouvelle entrée et marquer l’ancienne remplacée, avec motif et documents impactés. Extraire une décision longue en document dédié seulement si cela facilite réellement la lecture.

## 2. Décisions actées

| ID | Décision | Conséquence |
| --- | --- | --- |
| DEC-001 | Nom produit/projet : ÉCHAP | Utiliser cette identité dans les documents et le produit |
| DEC-002 | Assistant administratif professionnel pour la France | Couvrir administration, fiscalité, comptabilité, juridique, réglementaire et recouvrement ; pas de réduction au seul ledger |
| DEC-003 | Conversation et visualisation ultra minimaliste | Ne pas construire un ERP ; cinq vues demandées dans la spécification |
| DEC-004 | Self-service avec option d’intervention d’un expert-comptable partenaire | Faire examiner le cadre réel ; ne pas promettre une certification légale par l’outil |
| DEC-005 | Simplicité, sécurité, qualité et conformité sans compromis | Un délai de sprint ne justifie pas une ouverture risquée |
| DEC-006 | Harnais custom minimal, exécution et calculs encadrés | Permissions et validations en code, pas de dépendance à un prompt seul |
| DEC-007 | Modèles interchangeables, un fournisseur d’inférence unique | OpenRouter envisagé pour le MVP ; sélection des modèles par les évaluations, raisonnement renforcé seulement si utile |
| DEC-008 | Minimisation/anonymisation systématique et exigence zéro rétention | Conformité à démontrer par route ; pas de flux sensible tant que les garanties ne sont pas établies |
| DEC-009 | Objectif V2 : inférence en France et datacenters écologiques | Comparer garanties et impacts ; ne préjuge pas de l’hébergement de toutes les données |
| DEC-010 | Démarrer avec Paperasse comme brique de réemploi et le fiabiliser | Auditer, versionner et réutiliser utilement ; ÉCHAP n’est pas un renommage de Paperasse |
| DEC-011 | Cibles sprint 1 élargies selon PERIMETRE.md | Micro toutes activités éligibles, BNC, sociétés IS, collaborations libérales ciblées et SCI ; gestion courante et déclarations |
| DEC-012 | Pour médecins, vétérinaires et avocats : collaboration libérale au sprint 1 | Administration de leur activité uniquement, pas dossiers ni actes métier |
| DEC-013 | SCI : alignement sur Paperasse au sprint 1 | Frontière exacte à établir par audit doc/code/tests ; pas d’exhaustivité déclarative déduite des références |
| DEC-014 | Imports CSV/OFX au sprint 1 | Aucun agrégateur bancaire ni interface BankProvider anticipée |
| DEC-015 | Pas d’intégration métier externe au sprint 1, sauf TESE | Stripe, signature, email connecté, agrégation et transmission fiscale après ce sprint |
| DEC-016 | TESE avancé au sprint 1 pour les mandataires éligibles | Exception explicite à DEC-015 ; accès autorisé et éligibilité non encore démontrés |
| DEC-017 | Salariés via TESE au sprint 2 | Vérifier les cas éligibles ; ne pas supposer que TESE remplace toute la fonction RH |
| DEC-018 | Générer les déclarations, sans dépôt fiscal au sprint 1 | Export et statut « non déposé » ; formalités sociales TESE isolées comme exception |
| DEC-019 | Web + Telegram comme premiers canaux souhaités | Calendrier exact Telegram à arbitrer ; pas de promesse d’intégration S1 implicite |
| DEC-020 | Freemium et facturation à l’acte | Prix, quotas, actes payants et paiement à arbitrer ; pas d’abonnement obligatoire ajouté |
| DEC-021 | Budget récurrent MVP inférieur à 100 €/mois et recours au local | Mesurer infra, inférence, stockage et services ; ne pas confondre avec coût total de développement |
| DEC-022 | Solo avec agents IA, travail parallèle et docs-as-code | Instructions communes, tâches avec responsables, décisions et preuves versionnées |
| DEC-023 | Open core ; licence à décider plus tard | Ne pas créer de licence arbitraire ; vérifier néanmoins celles des briques réutilisées |
| DEC-024 | Objectif initial : MVP en une semaine ; intégrations majoritairement après | Conserver l’ambition, rendre visibles les dépendances ; pas d’engagement de conformité universelle à J7 |
| DEC-025 | MVP : un seul utilisateur par entreprise, décision du 2026-11-10 | Plusieurs testeurs et entreprises disposent d’espaces authentifiés et isolés ; accès partagés, invitations, rôles collaboratifs et accès direct d’un expert-comptable viennent après le MVP, sans date fixée. Précise DEC-004 sans supprimer la revue professionnelle nécessaire |
| DEC-026 | Ajouter un MTP, Minimum Testable Product, avant le MVP, décision du 2026-11-10 | Première enveloppe web hébergée de Paperasse, utilisable sans Claude Code, agent local ni installation chez le testeur ; le MVP n’est pas réduit ni déclaré livré par ce jalon |
| DEC-027 | MTP : données métier fictives uniquement | Aucun document réel ni compte métier de production ; les données minimales d’accès des testeurs et les secrets techniques restent protégés. Les garanties nécessaires avant données sensibles réelles restent celles du MVP |
| DEC-028 | MTP : six skills et connecteurs existants de Paperasse | Inclure comptable, fiscaliste, notaire, contrôleur fiscal, commissaire aux comptes et syndic ; connecteurs en sandbox lorsqu’elle existe, sinon simulation explicite. Aucun effet de production ni ajout TESE ; ne modifie pas les restrictions de production de DEC-015 |
| DEC-029 | MTP : privilégier la rapidité sans exigence France, souveraineté ni chiffrement spécifique | Hébergement à choisir librement ; maintenir HTTPS, accès protégé, secrets côté serveur et séparation des testeurs. Aucun chiffrement applicatif sur mesure ni dossier de souveraineté requis pour le test fictif |
| DEC-030 | MTP : base agent, harnais et infrastructure à comparer avant choix | Réemploi prioritaire d’un runtime/SDK adapté ; DEC-006 ne rend pas le harnais custom préalable au MTP. Pas de nouveau ledger ni de moteurs métier à reconstruire pour ce jalon |
| DEC-031 | Coordination autonome des sessions via verrous locaux par fichier, décision du 2026-11-10 | Remplacement de tout rôle de coordonnateur central par un verrouillage advisory atomique (`python3 tools/agent_lock.py`, base SQLite privée dans `.git`) ; les sessions indépendantes réservent leurs fichiers cibles avant écriture et les libèrent après, permettant des écritures concurrentes sur des fichiers disjoints et sérialisant les écritures concurrentes sur un même fichier sans intervention humaine |

| DEC-032 | Choix de stack et hébergement MTP : Python Streamlit et déploiement Streamlit Cloud, décision du 2026-11-17 | Enveloppe web Streamlit rapide pour le chat, l’upload de pièces fictives, l’exécution des scripts et le téléchargement des restitutions ; hébergement cloud 24/7 sur Streamlit Community Cloud avec secrets côté serveur |
| DEC-033 | Inférence MTP : OpenRouter côté serveur, modèle par défaut Gemini 2.5 Flash, décision du 2026-11-17 | Clé OPENROUTER_API_KEY gérée strictement côté serveur (fichier .env en local, secrets Streamlit en cloud), sans exposition dans l’interface utilisateur ; modèle ultra-rapide et économique par défaut (`google/gemini-2.5-flash`) |
| DEC-034 | Emplacement des composants Paperasse réemployés : packages/paperasse/, décision du 2026-11-17 | Intégration des 6 skills, référentiels de données (PCG 2026, liasse), templates et scripts de calcul sous packages/paperasse/ pour un MTP auto-contenu |
| DEC-035 | Sources publiques et connecteurs MTP : sources publiques réelles avec cache local sur serveur, connecteurs privés différés, décision du 2026-11-17 | Pas de Qonto, Stripe ni Pennylane au MTP ; intégration réelle des sources publiques (référentiel PCG 2026 embarqué, API recherche-entreprises / Annuaire des entreprises avec cache SQLite local sur le serveur pour accès ultra-rapide) |

Ces décisions ajoutent une expérimentation préalable. Les sprints 1 et 2 existants restent ceux du MVP et de sa suite ; ils ne sont pas renommés en MTP. DEC-024 conserve l’objectif historique d’une semaine pour le MVP : aucune date ni enveloppe budgétaire propre au MTP n’est fixée par cet ajout. Les thèmes privés et de copropriété de Paperasse sont expérimentés au MTP, sans étendre automatiquement la cible professionnelle du MVP.

## Coordination autonome des sessions indépendantes (DEC-031)

À la suite de l’arbitrage du porteur rejetant l’introduction d’un rôle de coordonnateur (humain ou agent) pour piloter des sessions indépendantes, le protocole de [AGENTS.md](../AGENTS.md) s’appuie sur un outil local de verrouillage par fichier (`tools/agent_lock.py`).
Chaque session réserve automatiquement les fichiers qu'elle doit modifier, attend si un fichier est temporairement occupé par une autre session, effectue sa modification et libère le verrou. Les registres partagés (`docs/SUIVI.md` et `docs/DECISIONS.md`) sont mis à jour selon la même méthode. Les arbitrages produit, risques et budget restent la prérogative du porteur.

## 3. Propositions non adoptées

| ID | Proposition | Critère d’arbitrage |
| --- | --- | --- |
| PROP-01 | Monolithe modulaire, TypeScript par défaut ; Python ciblé seulement si besoin prouvé | Note dans ARCHITECTURE.md, coût d’exploitation, réemploi et tests |
| PROP-02 | Web comme canal effectif initial, Telegram ensuite | Cohérence avec DEC-015 et coût/confidentialité du canal |
| PROP-03 | Réutiliser un moteur/ledger existant si adapté plutôt que fabriquer un moteur fiscal complet | Audit fonctionnel, invariants, conformité, licence et maintenabilité |

Les propositions historiques pnpm/Turborepo/Next.js/PostgreSQL/RLS/sidecar Python et ledger maison ne sont pas adoptées. Pas de scaffold à produire sur cette seule base.

## 4. Vérifications et choix ouverts

| ID | Question ou preuve attendue | Responsable de l’arbitrage / tâche |
| --- | --- | --- |
| OUV-01 | URL et commit du fork Paperasse déclaré disponible ; capacités par profil, SCI notamment | Porteur + ECH-003 |
| OUV-02 | Statuts mandataires couverts par TESE, modalités de mandat, accès autorisé et résultats récupérables | Porteur + ECH-004 |
| OUV-03 | Stack, persistance et stratégie ledger | Porteur après ECH-005 |
| OUV-04 | Hébergement et modalités d’exploitation ; Infomaniak candidat, pas décision | Porteur après ECH-006 |
| OUV-05 | Routes OpenRouter réellement compatibles avec confidentialité, rétention et transferts | ECH-006 ; blocage sécurité |
| OUV-06 | Catalogue complet obligations/actions par activité, forme, fiscalité, social, TVA et millésime | ECH-002 + revue compétente |
| OUV-07 | Cadre self-service, actes réglementés, assurance, partenaires et données sensibles | ECH-007 ; validation compétente |
| OUV-08 | Calendrier Telegram et extension aux canaux mobiles | Porteur + ECH-016 |
| OUV-09 | Prix des actes, plafonds gratuits, coût cible et moyens de paiement | Porteur + ECH-008 |
| OUV-10 | Employeurs micro, associés avec contrat de travail et portée de l’exclusion des stagiaires | Porteur + ECH-002 |
| OUV-11 | Frontière SCI/professionnel et thèmes patrimoniaux privés ou copropriété de Paperasse | Porteur après ECH-003 |
| OUV-12 | Niveaux d’autonomie, validations et plafonds opérationnels autorisés | Porteur + ECH-009 |
| OUV-13 | Base agent/harnais, stack, inférence et hébergement les plus rapides à exploiter pour le MTP | Porteur après comparaison ECH-028 ; aucun choix adopté |
| OUV-14 | Version Paperasse, capacités exposables et sandboxes réellement disponibles ; simulations nécessaires | ECH-027 et ECH-030 |
| OUV-15 | Date, budget, nombre de testeurs et durée de conservation des essais MTP | Porteur + ECH-028/031 ; ne pas déduire ces valeurs du MVP |

## 5. Format pour les prochaines entrées

Identifiant ; date ; statut ; contexte ; options ; décision ou preuve attendue ; auteur/responsable ; conséquences et risques ; tâches et documents impactés ; condition de réexamen ; décision remplacée le cas échéant.

Les seuils, taux, tarifs fournisseurs et interprétations légales vont dans un registre de règles/sources vérifiées, pas dans ce tableau comme vérités permanentes. Voir [DEPENDANCES.md](DEPENDANCES.md).
