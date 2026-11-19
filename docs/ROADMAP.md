# ÉCHAP — Roadmap initiale

Statut : objectifs de travail, pas garantie de disponibilité. Date : 2026-11-10.

## 1. Logique de livraison

Un jalon **MTP expérimental précède le MVP** (DEC-026 à DEC-030). Il vise à rendre rapidement accessibles les six skills existants de Paperasse et ses connecteurs de test, exclusivement sur données fictives, sans refonte des moteurs ni nouvelles fonctionnalités métier.

L’objectif historique d’un premier MVP en une semaine est conservé (DEC-024), avec son périmètre large et ses exigences de qualité, de sécurité et de conformité. Il ne constitue ni une preuve de faisabilité ni un engagement à livrer MTP et MVP ensemble dans cette semaine. Date, budget et nombre de testeurs du MTP restent à arrêter.

Ne pas réduire le périmètre MVP sans décision explicite. Rendre visibles les capacités demandées, les dépendances et les fonctions effectivement validées. Une fonction bloquée ne peut pas être présentée comme livrée pour tenir une date.

Les sprints 1 et 2 ci-dessous sont ceux du MVP, relatifs au démarrage effectif à convenir ; aucune date de mise en production n’est fixée par ce document.

## 2. Fondations — livrable documentaire courant

- Vision et principes d’ÉCHAP, distinct de sa brique Paperasse.
- Périmètre et spécification de tous les domaines administratifs.
- Architecture proposée et choix encore ouverts ; menaces et conditions de confidentialité.
- Modèle économique et dépendances externes sans tarifs inventés.
- Décisions, tâches et conventions pour humains/agents en parallèle.

Cette étape ne vaut pas validation d’une stack, d’un moteur comptable ni d’un hébergement. Voir [SUIVI.md](SUIVI.md) pour l’avancement réel.

Arbitrage transversal ECH-016 : fixer le calendrier Telegram selon confidentialité, coût et parcours. Sa réalisation suivra cet arbitrage ; aucun horizon S1 ou S2 n’est imposé ici.

## 3. MTP — étape expérimentale avant le MVP

### Objectif et limites

- Accès web aux 6 skills existants (`comptable`, `fiscaliste`, `notaire`, `controleur-fiscal`, `commissaire-aux-comptes`, `syndic`).
- Raccordement des connecteurs existants (Qonto, Stripe, Pennylane, sources publiques) en sandbox ou simulation.
- Données exclusivement fictives : aucun document, compte ni flux réel.
- Interface web simple : chat, dépôt de pièces fictives, téléchargement des restitutions. Pas d'installation locale pour le testeur.

### Ordre de travail du MTP

| Séquence | Résultat attendu | Tâche |
| --- | --- | --- |
| Inventorier le réemploi | Version/commit, licences, smoke tests des scripts, état des connecteurs | ECH-027 |
| Décider le socle technique | Base agent, runtime/harnais, stack, hébergement et budget MTP | ECH-028 |
| Déployer l'accès web | Chat web hébergé, espaces isolés, dépôt et restitutions de fichiers | ECH-029 |
| Raccorder les connecteurs | Sandbox fictive ou simulation visible | ECH-030 |
| Recette et retours | Validation de l'accessibilité des 6 skills et connecteurs sur cas fictifs | ECH-031 |

Les critères d'acceptation détaillés du MTP sont définis dans [PRODUIT.md](PRODUIT.md).

## 4. MVP — sprint 1 : assistant administratif complet, premières capacités vérifiables

### Objectifs demandés

- Couvrir les profils micro, BNC, sociétés IS, collaborations libérales ciblées et SCI définis dans [PERIMETRE.md](PERIMETRE.md).
- Gestion courante et génération des déclarations applicables, sans dépôt fiscal.
- MVP : un utilisateur par entreprise ; plusieurs testeurs dans des espaces authentifiés et isolés, sans accès partagé ni invitations.
- Chat, visualisation minimale, documents, devis/factures/honoraires, obligations et calendrier.
- Comptabilité et fiscalité par profil, rapprochement CSV/OFX, exports applicables et contrôles.
- Préparation juridique d’entreprise, décisions sociales, recouvrement et dossiers de vérification à partir d’informations fournies.
- Gestion des dirigeants ; TESE pour mandataires éligibles, seule exception aux intégrations métier externes de production en S1 MVP. Les connecteurs expérimentaux du MTP ne modifient pas cette restriction.
- Harnais custom minimal selon DEC-006, évaluation des modèles, mesure coût/latence et protections avant données réelles : minimisation et zéro rétention effectif démontrés pour chaque route concernée.

### Ordre de travail proposé

| Séquence | Résultat vérifiable | Tâches principales |
| --- | --- | --- |
| Qualifier et lever les blocages | Matrice profils/obligations ; accès Paperasse ; preuve ou blocage TESE et inférence | ECH-002 à ECH-008 |
| Fixer le socle minimal | Choix explicites, contrats d’action, contexte et permissions | ECH-005, ECH-009, ECH-010 |
| Livrer par parcours | Document/import → action contrôlée → résultat consultable ; parcours non comptables également | ECH-010 à ECH-015 |
| Recetter et préparer l’ouverture | Preuves métier/sécurité/coûts, limites visibles, retours utilisateurs | ECH-017, ECH-018 |

Les recherches réglementaires, l’audit OSS, l’expérience utilisateur et l’étude TESE peuvent avancer en parallèle avec responsabilités et fichiers séparés. Une démonstration bout-en-bout valide le câblage mais ne remplace pas la couverture demandée.

### Dépendances bloquantes

- TESE : éligibilité précise, adhésion et mécanisme d’accès autorisé ; aucune API publique n’a été démontrée.
- Inférence : route de traitement réellement compatible avec les garanties demandées.
- Matrice réglementaire et tests des déclarations : les skills de Paperasse ne suffisent pas à prouver la conformité.
- Données sensibles : qualification des obligations de secret, santé et transferts ; pas de données réelles avant les protections correspondantes.

Si une dépendance ne peut être levée dans la semaine, conserver la tâche bloquée et demander un arbitrage. Une préparation guidée n’est pas un remplacement décidé de l’intégration TESE.

## 5. MVP — immédiatement après le sprint 1 / sprint 2

- Étendre le traitement des salariés via TESE pour les situations éligibles ; inventorier les obligations qui restent hors service.
- Prioriser et intégrer banque, Stripe, email/collecte/OCR, signature et transmission fiscale après comparaison des solutions et accès réels.
- Mettre en place les sources publiques de vérification d’entreprises et leur suivi de fraîcheur.
- Étudier la mise en relation et l’offre optionnelle de partenaires selon les besoins constatés. Les revues compétentes nécessaires aux sorties sensibles sont organisées avant l’ouverture réelle concernée, sans attendre ce chantier.

Les intégrations sont un objectif rapproché, pas une promesse que tous les contrats et accès seront obtenus au sprint 2. Les obligations actuelles de facturation électronique doivent être identifiées : l’absence d’intégration ne dispense pas l’utilisateur de les respecter.

## 6. Extensions produit et V2

- Approfondir artisans, TPE de services jusqu’à 2 M€ de CA et 10 salariés, artistes-auteurs et e-commerce de volume modéré, sans restreindre rétrospectivement les profils déjà demandés.
- Étudier après le MVP l’accès partagé entre utilisateurs d’une entreprise et l’accès direct d’un expert-comptable, sans date de livraison fixée.
- Inférence en France et datacenters écologiques, avec preuves techniques et environnementales ; réexaminer confidentialité, coût et qualité des modèles.
- Canaux mobiles dédiés, WhatsApp/Signal et options d’hébergement à étudier si le besoin est confirmé.
- Définir la frontière open core et la licence avant publication des composants concernés.

## 7. Conditions de passage à une bêta réelle — hors recette MTP

Ces portes concernent l’usage de données réelles et les sorties destinées à un usage réel ; elles ne sont pas des prérequis supplémentaires à la recette fictive MTP de la section 3.

1. Profil et opérations de chaque testeur explicitement couverts ; limites et statuts annoncés.
2. Sources, règles, tests et revue compétente pour les sorties engageantes.
3. Authentification et autorisation objet/action vérifiées ; plusieurs espaces d’entreprise isolés et tests d’accès croisés, confirmations, audit, sauvegarde et restauration vérifiés.
4. Confidentialité d’inférence démontrée ou flux sensible désactivé ; aucun contournement implicite.
5. Accès externes autorisés, absence de faux accusé, doublons et reprises maîtrisés.
6. Mesure et limites permettant de tenir le budget ; aucune facturation opaque.
7. Parcours administratifs non comptables recettés autant que le traitement comptable.

Les défauts bloquants sont corrigés avant ouverture. Un test sur données synthétiques peut avancer pendant la résolution d’un blocage sans être assimilé à une disponibilité en production.
