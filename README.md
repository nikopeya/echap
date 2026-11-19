# ÉCHAP

**L’assistant qui libère les entrepreneurs de la paperasse.**

ÉCHAP est un projet d’assistant IA pour les professionnels établis en France : administration, comptabilité, fiscalité, facturation, obligations réglementaires, juridique de l’entreprise et recouvrement. La comptabilité est une composante du produit, pas sa définition.

L’expérience repose sur une conversation et un outil de visualisation minimaliste. L’utilisateur délègue ; des méthodes et actions contrôlées exécutent le travail ; les décisions engageantes restent explicites et traçables.

## État du projet

Cadrage initial au **10 novembre 2026**. Ce dépôt accueille la réflexion produit, la recherche, les décisions, le suivi et, ensuite, le développement. Il ne contient pas encore d’application ni de moteur métier validé.

Les documents distinguent les **arbitrages actés**, les **propositions**, les **hypothèses** et les **vérifications à mener**. Un objectif de sprint n’est pas une déclaration de capacité livrée.

**Paperasse n’est pas ÉCHAP.** C’est une brique open source envisagée pour accélérer le projet, à auditer, réutiliser et fiabiliser au même titre que d’autres composants existants. La synthèse historique est conservée sans modification comme matériau de recherche, pas comme source normative.

## Commencer ici

| Document | Rôle |
| --- | --- |
| [Vision et principes](docs/VISION.md) | Ambition, expérience, cible, non-objectifs et contraintes structurantes |
| [Périmètre](docs/PERIMETRE.md) | MTP, populations et domaines MVP, inclus/exclus et frontières à préciser |
| [Spécification produit](docs/PRODUIT.md) | Parcours, vues, exigences et critères d’acceptation initiaux |
| [Architecture](docs/ARCHITECTURE.md) | Socle proposé, harnais, exécution déterministe et note de choix de stack |
| [Sécurité et confidentialité](docs/SECURITE.md) | Menaces, protections, données sensibles et conditions d’ouverture |
| [Économie](docs/ECONOMIE.md) | Freemium, actes, budget et indicateurs de coût |
| [Dépendances et réemploi](docs/DEPENDANCES.md) | Paperasse, TESE, composants candidats et vérifications externes |
| [Décisions](docs/DECISIONS.md) | Décisions actées, propositions et questions encore ouvertes |
| [Roadmap](docs/ROADMAP.md) | Objectifs des sprints et portes de validation |
| [Suivi](docs/SUIVI.md) | Backlog initial, responsabilités et coordination des travaux |
| [Identité de marque](docs/marque.md) | Plateforme, ligne éditoriale, charte graphique et règles d’interface |
| [Conventions de contribution](AGENTS.md) | Règles communes aux humains et agents IA |

## Étapes produit

| Étape | Objectif et limite |
| --- | --- |
| **MTP — Minimum Testable Product** | Première enveloppe web hébergée des six skills et connecteurs existants de Paperasse ; données métier fictives uniquement, sandboxes ou simulations visibles. Aucun agent, Claude Code ni installation requis chez le testeur. |
| **MVP** | Assistant administratif professionnel complet selon le périmètre demandé, avec les validations nécessaires avant usage réel ; ne se réduit pas aux capacités du MTP. |
| **Suite** | Extensions et intégrations selon les arbitrages de roadmap ; l’ajout du MTP ne déplace pas automatiquement les engagements existants. |

La priorité immédiate est le MTP. Agent, harnais, stack et hébergement restent à choisir pour le réemploi et la rapidité ; aucune exigence France, souveraineté ou chiffrement spécifique à ce stade. HTTPS, accès protégé, secrets côté serveur et séparation des testeurs restent requis. Les sprints 1 et 2 ci-dessous désignent le MVP et sa suite, pas le MTP. Voir le [périmètre](docs/PERIMETRE.md) et la [roadmap](docs/ROADMAP.md).

## Arbitrages essentiels du MVP et de la cible

- France professionnelle uniquement ; simplicité, qualité, sécurité et conformité sans compromis de calendrier.
- Assistant administratif complet, pas ERP à paramétrer ni simple outil comptable.
- Sprint 1 large : micro-entrepreneurs toutes activités éligibles, BNC, sociétés à l’IS sans équipe salariée hors associés/mandataires, collaborations libérales ciblées et SCI ; voir la matrice de périmètre.
- Gestion courante et génération des déclarations ; pas de dépôt fiscal en ligne au sprint 1.
- MVP : un utilisateur par entreprise, avec des espaces sécurisés isolés pour plusieurs testeurs ; accès partagés et expert-comptable dans l’outil après le MVP ([décision](docs/DECISIONS.md)).
- TESE : exception métier externe explicite dès le sprint 1 pour les mandataires éligibles ; salariés au sprint 2. Éligibilité et accès autorisé restent à vérifier.
- Autres intégrations métier après le sprint 1 ; imports locaux CSV/OFX et documents au départ.
- Harnais custom minimal, modèles interchangeables, fournisseur d’inférence unique : OpenRouter envisagé pour le MVP sous conditions de confidentialité démontrées.
- Freemium et paiement à l’acte ; budget récurrent MVP inférieur à 100 €/mois ; développement local privilégié.
- Open core ; licence et frontière de publication à décider ultérieurement. Aucune licence n’est attribuée par ces documents.

## Travailler sur le projet

1. Lire [AGENTS.md](AGENTS.md), puis le document du domaine concerné.
2. Avant toute écriture, réserver les fichiers avec `python3 tools/agent_lock.py acquire --session "<id_session>" --task "<id_tache>" <fichiers...>` selon [AGENTS.md](AGENTS.md). Une recherche ou revue strictement en lecture seule n’exige pas de verrou.
3. Distinguer une recherche d’une décision ; consigner les décisions dans [DECISIONS.md](docs/DECISIONS.md) sous verrou.
4. Mettre à jour l'avancement dans [SUIVI.md](docs/SUIVI.md) sous verrou ; ne pas publier ou intégrer (commit, push) sans demande explicite du porteur.

Aucun framework, stockage, hébergement ou moteur comptable n’est adopté implicitement par l’arborescence documentaire. Aucun script de lint, de typecheck ou de test applicatif n’est encore défini.
