# ÉCHAP — Suivi et backlog initial

Date : 2026-11-10. Ce fichier suit le travail réel ; [ROADMAP.md](ROADMAP.md) décrit les objectifs et [DECISIONS.md](DECISIONS.md) les arbitrages.

## 1. État initial

- Dépôt sans application au début de la session ; une synthèse de recherche Paperasse préexistante, conservée intacte.
- Socle documentaire d’ÉCHAP créé dans cette session ; cohérence et contrôles documentaires vérifiés.
- Aucun moteur, intégration, route d’inférence ni sortie réglementaire n’est déclaré livré.
- Solo + agents IA ; URL du fork utilisateur, accès techniques et expertises de revue restent à organiser. Ne pas mettre de secrets dans le suivi.

## 2. Règles de pilotage

Statuts : **à faire**, **en cours**, **en pause**, **bloqué**, **en revue**, **terminé**, **abandonné**. Priorités : **P0** préalable bloquant ; **P1** objectif du sprint ; **P2** suite ou amélioration.

La procédure canonique de coordination entre sessions indépendantes est définie dans [AGENTS.md](../AGENTS.md) (DEC-031). Elle repose sur un outil de verrouillage local par fichier (`tools/agent_lock.py`) : toute session réserve ses fichiers cibles avant modification et libère le verrou dès achèvement. Plusieurs sessions peuvent modifier des fichiers distincts en parallèle ; les accès concurrents sur un même fichier sont automatiquement mis en file d’attente sans intervention humaine ni rôle de coordonnateur central.

Pour consigner le démarrage, l’avancement ou la fin d’une tâche dans ce suivi, ou un arbitrage dans [DECISIONS.md](DECISIONS.md), la session réserve le fichier concerné (`docs/SUIVI.md` ou `docs/DECISIONS.md`), effectue sa mise à jour et libère le verrou. Les recherches et revues en lecture seule ne requièrent aucun verrou.

Une tâche terminée possède un résultat vérifié. Une tâche bloquée ou en pause indique son motif et sa prochaine action ; ses verrous applicatifs sur les fichiers de travail sont libérés si le travail est suspendu, afin de ne pas bloquer inutilement les autres sessions.

## 3. Backlog et priorité actuelle

Le prochain jalon est le **MTP avant le MVP** : prendre ECH-027 à ECH-031 pour inventorier l’existant, choisir son enveloppe et le rendre testable sur données fictives. Les tâches existantes S1/S2 restent celles du MVP et de sa suite, sans réduction du périmètre ni déplacement automatique. Leurs portes d’usage réel ne deviennent pas toutes des prérequis de la recette MTP ; leurs résultats utiles peuvent être réemployés.

| ID | Priorité / horizon | Travail et résultat attendu | Dépendances | Responsable | Statut |
| --- | --- | --- | --- | --- | --- |
| ECH-001 | P0 / fondations | Créer vision, périmètre, produit, architecture proposée, sécurité, économie, décisions et pilotage | Discussion de cadrage | Agent principal de cette session | Terminé |
| ECH-002 | P0 / S1 | Matrice profils × obligations × opérations, frontières ouvertes arbitrées et registre de règles/sources | DEC-011, OUV-06/10 | À attribuer ; arbitrage porteur et revue métier | À faire |
| ECH-003 | P0 / S1 | Audit versionné du fork Paperasse : doc/code/tests, SCI, déclarations, calculs, formats, licences et réemploi | URL/commit du fork à fournir | À attribuer | À faire |
| ECH-004 | P0 / S1 | Preuve d’éligibilité mandataires et voie d’intégration TESE autorisée ; sinon blocage explicite | Accès/adhésion/mandat, sources officielles | À attribuer ; accès porteur | À faire |
| ECH-005 | P0 / S1 | Choisir stack, stockage et socle comptable après comparaison OSS et essai ciblé ; enregistrer l’arbitrage | ECH-002/003, note architecture | À attribuer ; décision porteur | À faire |
| ECH-006 | P0 / S1 | Dossier confidentialité/inférence/hébergement, routes et replis, preuve zéro rétention, minimisation et menaces | Conditions fournisseurs et catégories de données | À attribuer ; décision porteur | À faire |
| ECH-007 | P0 / S1 | Qualifier self-service, actes réglementés, données sensibles, responsabilités, assurances et revue partenaire | ECH-002, expertise compétente | À attribuer | À faire |
| ECH-008 | P0 / S1 | Budgets instrumentables, quotas et benchmark coût/latence ; hypothèses freemium/actes à tester | ECH-005/006, volumes testeurs | À attribuer | À faire |
| ECH-009 | P1 / S1 | Définir contrats d’actions, droits objet/action, confirmations, audit et reprise pour un utilisateur par entreprise ; harnais minimal | ECH-002/005/006, DEC-025 | À attribuer | À faire |
| ECH-010 | P1 / S1 | Profil entreprise, authentification et isolation des espaces, documents et imports CSV/OFX avec provenance et doublons | ECH-005/006/009, DEC-025 | À attribuer | À faire |
| ECH-011 | P1 / S1 | Comptabilité et déclarations par profil, calculs/contrôles/exports testés ; pas dépôt fiscal | ECH-002/003/005/010 et revue métier | À attribuer | À faire |
| ECH-012 | P1 / S1 | Devis/factures/honoraires/avoirs/acompte, règles de numérotation et formats validés | ECH-002/009/010 | À attribuer | À faire |
| ECH-013 | P1 / S1 | Administration, calendrier, projets juridiques, décisions sociales, recouvrement et vérifications sur pièces fournies | ECH-002/007/009/010 | À attribuer | À faire |
| ECH-014 | P1 / S1 | Intégrer TESE pour mandataires éligibles : confirmation, suivi, récupération de résultats et rapprochement | ECH-004/006/009 ; accès autorisé indispensable | À attribuer | À faire |
| ECH-015 | P1 / S1 | Chat web et cinq vues minimales, prévisualisations, confirmations accessibles et statuts fiables | Stack choisie et contrats des parcours | À attribuer | À faire |
| ECH-016 | P1 / arbitrage | Fixer calendrier Telegram et contraintes du canal, sans le considérer déjà intégré ou reporté | DEC-019, ECH-006 | Porteur, étude à attribuer | À faire |
| ECH-017 | P0 / ouverture | Corpus synthétique, résultats attendus validés, tests métier/sécurité/reprise/coûts et recette par profil ; tester les accès croisés entre entreprises | Parcours ECH-009 à ECH-015 ; démarrer le corpus en parallèle | À attribuer ; revues compétentes | À faire |
| ECH-018 | P1 / bêta | Confirmer les testeurs, espaces individuels isolés, tâches prioritaires, consentements, recette, limites et retours ; décision d’ouverture | ECH-006/007/017 pour données réelles | Porteur + réalisation à attribuer | À faire |
| ECH-019 | P1 / S2 | Étendre aux salariés via TESE, exceptions et besoins RH résiduels inventoriés | ECH-004/014, règles salariés à valider | À attribuer | À faire |
| ECH-020 | P1 / après S1 | Comparer puis intégrer banque, Stripe, email/OCR, signature, dépôts fiscaux et sources publiques | ECH-006/008, accès et contrats ; priorisation porteur | À attribuer | À faire |
| ECH-021 | P2 / V2 | Étude inférence France, impact environnemental et migration fournisseur/modèles | Mesures qualité/coût/confidentialité | À attribuer | À faire |
| ECH-022 | P2 / avant publication | Choisir licence ÉCHAP et frontière open core ; vérifier compatibilité des reprises | Inventaire des licences ECH-003/005 | Porteur + revue compétente | À faire |
| ECH-023 | Documentation | Harmoniser la terminologie « testeur » dans VISION.md, PRODUIT.md, ECONOMIE.md et SUIVI.md | Demande utilisateur | Agent principal de cette session ; 2026-11-10 | Terminé |
| ECH-024 | Documentation | Intégrer la décision : un utilisateur par entreprise au MVP, espaces isolés et collaboration ultérieure | Arbitrage du porteur | Agent principal de cette session ; 2026-11-10 | Terminé |
| ECH-025 | P2 / après MVP | Étudier invitations, accès partagés et rôles collaboratifs, dont accès direct d’un expert-comptable | DEC-025 ; calendrier et besoins à arbitrer | À attribuer | À faire |
| ECH-026 | Documentation | Ajouter le MTP avant le MVP, ses décisions, conditions de test et tâches, sans réduire le MVP | Arbitrage du porteur | Agent principal de cette session ; 2026-11-10 | Terminé |
| ECH-027 | P0 / MTP | Inventorier/versionner les six skills et connecteurs Paperasse, vérifier licences, entrées/sorties et smoke tests ciblés des scripts exposables | DEC-026 à DEC-028 ; amont auditable sans attendre l’URL du fork | Session ses_mtp_dev ; 2026-11-17 | Terminé |
| ECH-028 | P0 / MTP | Comparer puis faire choisir base agent/harnais, stack, inférence et hébergement ; chiffrer délai/coût et fixer limites d’essai | Premier inventaire ECH-027, DEC-029/030 ; arbitrage porteur | Porteur (DEC-032 à DEC-035) ; 2026-11-17 | Terminé |
| ECH-029 | P1 / MTP | Enveloppe web hébergée : chat, accès protégé, espaces isolés, pièces fictives et fichiers restitués, raccordement contrôlé des six skills | ECH-027/028 ; aucune installation d’agent chez le testeur | Session ses_mtp_dev ; 2026-11-17 | Terminé |
| ECH-030 | P1 / MTP | Raccorder les connecteurs existants en sandbox vérifiée ou simulation visible ; tester nominal/erreur sans accès ni effet métier de production | ECH-027/028/029 ; clés de test serveur seulement si nécessaires | Session ses_mtp_dev ; 2026-11-17 | Terminé |
| ECH-031 | P0 / ouverture MTP | Recetter MTP-01 à MTP-08, six skills et connecteurs sur cas fictifs ; isolation, restitutions, coût/latence et retours testeurs | ECH-029/030 ; pas de validation réglementaire globale ni de TESE en prérequis | Session ses_mtp_dev ; 2026-11-17 | Terminé |
| ECH-032 | Documentation / coordination | Auditer et renforcer le protocole multi-agents ; corriger les ambiguïtés documentaires relevées | Demande du porteur, audits en lecture seule | Agent principal de cette session ; 2026-11-10 | Terminé |
| ECH-033 | Implémentation / transversal | Permettre aux sessions indépendantes de coordonner leurs écritures dans le même arbre sans coordonnateur permanent | Demande du porteur ; Python et SQLite locaux | Session `ECH-033` ; 2026-11-10 | Terminé |
| ECH-034 | P1 / transversal | Créer l'identité de marque ÉCHAP : plateforme, charte graphique, ton de voix, règles UI et assets vectoriels | DEC-001, DEC-003, EX-14 | Session ECH-034 ; 2026-11-19 | Terminé |
| ECH-035 | P1 / S1 | Implémenter le parcours d'Onboarding initial (PAR-01) : qualification entreprise, régimes fiscaux, dirigeant et échéances automatiques pour l'agent | ECH-010, PAR-01 | Session ses_e0afd ; 2026-11-19 | Terminé |
| ECH-036 | P1 / architecture | Découplage Utilisateur (personne physique) ⇄ Structures (personnes morales/activités), inscription sans entreprise obligatoire, support natif micro-entreprises et multi-entités collaboratives (N:M) | ECH-035, DEC-025 | Session ses_e0afd ; 2026-11-19 | Terminé |
| ECH-039 | P1 / UX | Onboarding Typeform pas-à-pas (1 seule question par écran, grands boutons clairs, barre de progression) | ECH-035, ECH-036 | Session ses_e0afd ; 2026-11-19 | Terminé |

Les tâches larges seront découpées au moment de les prendre ; ne pas répartir « toutes les déclarations » entre agents sans répartition de profils, fichiers et résultats attendus.

## 4. Réservations et travaux en cours

La coordination des écritures s'effectue en temps réel via `python3 tools/agent_lock.py` : l'état instantané des verrous actifs est consultable avec `python3 tools/agent_lock.py status`.

Ce tableau consigne les chantiers déclarés par les sessions : **tâche ; mode ; jalon ; session et date ; fichiers concernés ; statut**.

Aucun verrou actif à cet instant. ECH-033 est terminé ; les fichiers touchés sont libérés.

## 5. Critères de résultat pour les premiers blocages

### MTP — vérifications proportionnées au test fictif

- ECH-027 : six skills et ensemble des connecteurs inventoriés sur une version identifiée ; documentation, scripts, tests exécutés et limites distincts. Sources, licences et garde-fous minimaux vérifiés. Ne pas remplacer cet inventaire ciblé par un audit exhaustif de toute la cible MVP.
- ECH-028 : options réellement comparées sur compatibilité Paperasse, effort d’enveloppe web, coût, isolation et exploitation ; choix explicite du porteur, budget et plafonds avant dépenses. Aucun harnais maison ni hébergeur imposé.
- ECH-029 : un testeur accède aux six domaines depuis un navigateur sans Claude Code, terminal ni clé d’inférence personnelle ; dépôt/restitution, accès séparés et erreurs vérifiés.
- ECH-030 : chaque connecteur inventorié possède un mode sandbox autorisé et fictif ou une simulation explicite ; preuves d’absence d’appels et d’effets métier de production. Aucune sandbox ni connexion réelle supposée.
- ECH-031 : recette MTP-01 à MTP-08 documentée avec résultats/échecs et retours ; pas de confusion entre test réussi, conformité métier et autorisation de traiter de vraies pièces.

### MVP — conditions de couverture et d’usage réel

- ECH-002 : chaque profil demandé possède une liste d’obligations, des périodes/sources et des opérations couvertes/non encore validées. Les arbitrages ne sont pas remplacés par des exclusions implicites.
- ECH-003 : commit épinglé, inventaire des fichiers utiles, limites démontrées, licence et test de chaque réemploi envisagé ; distinguer génération de document et conformité validée.
- ECH-004 : source d’éligibilité, conditions d’accès, preuves/autorisation et démonstration avec données de test si possible ; pas d’accès privé ou d’API supposée.
- ECH-005 : options et compromis documentés, expérience ciblée reproductible, décision explicite du porteur ; pas de scaffold avant choix.
- ECH-006 : inventaire des flux et données, opérateurs réels, conservation/transferts/replis, pièces contractuelles et réglages ; aucune garantie inférée d’une seule option marketing.
- ECH-007 : risques et limites qualifiés, interlocuteur compétent identifié, actions et blocages documentés ; pas de certification auto-déclarée.
- ECH-017 : preuves de contrôle indépendantes du modèle, cas d’échec et états inconnus couverts ; validation non comptable également exigée.

## 6. Livraison et preuves

Pour chaque résultat, la session consigne : tâche et session ; fichiers effectivement touchés ; base disponible ; changements et décisions associées ; vérifications réellement exécutées ; limites, dépendances et travaux suivants. Pour consigner dans ce fichier, elle acquiert le verrou sur `docs/SUIVI.md` avec `python3 tools/agent_lock.py acquire --session "<session>" --task "<tache>" docs/SUIVI.md` et le libère immédiatement après.

Une tâche ne peut être marquée « terminée » que si ses critères d’acceptation sont effectivement vérifiés. Aucune opération Git de publication ou d’intégration (commit, merge, push) n'est autorisée sans accord explicite du porteur.

Les tests automatisés de coordination sont exécutables avec :
```bash
python3 -m unittest discover -s tests -p 'test_agent_lock.py'
```

## 7. Historique initial

| Date | Événement | Preuve / état |
| --- | --- | --- |
| 2026-11-10 | Cadrage utilisateur : ÉCHAP, produit complet et exception TESE S1 | Décisions DEC-001 à DEC-024 ; aucune implémentation revendiquée |
| 2026-11-10 | Création du socle documentaire séparé de la synthèse Paperasse | ECH-001 terminé : README.md, AGENTS.md et dix documents docs/ ; revue de cohérence effectuée |
| 2026-11-10 | Vérification documentaire exécutée sans installation | 12 documents, 68 liens relatifs valides, références DEC/OUV/ECH résolues ; contrôles de whitespace et motifs de secrets sans anomalie |
| 2026-11-10 | ECH-023 : terminologie « testeur » harmonisée à la demande du porteur | VISION.md, PRODUIT.md, ECONOMIE.md et SUIVI.md ; recherche globale sans occurrence de l’ancienne terminologie, format vérifié ; aucune commande applicative configurée |
| 2026-11-10 | ECH-024 : décision DEC-025 et propagation du modèle d’accès MVP | README.md, DECISIONS.md, PERIMETRE.md, VISION.md, PRODUIT.md, ARCHITECTURE.md, SECURITE.md, ROADMAP.md et SUIVI.md ; 12 documents, 69 liens relatifs et références DEC/ECH vérifiés ; isolation maintenue, collaboration après MVP suivie par ECH-025 ; aucun test applicatif configuré |
| 2026-11-10 | ECH-026 : MTP ajouté avant le MVP, DEC-026 à DEC-030 | Les 12 documents existants mis à jour ; six skills et connecteurs sur données fictives, recette distincte et tâches ECH-027 à ECH-031 ; MVP préservé |
| 2026-11-10 | Vérification de la mise à jour MTP | 12 documents, 82 liens relatifs valides, références DEC/OUV/ECH/MTP uniques et résolues, format et motifs de secrets contrôlés ; revue en lecture seule et correction des ambiguïtés zéro rétention/données d’accès ; aucun test métier ou déploiement revendiqué |
| 2026-11-10 | ECH-032 : revue du dossier et clarification de la coordination | `AGENTS.md`, `README.md`, `docs/SUIVI.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`, `docs/DEPENDANCES.md` ; base disponible : arbre partagé sans commit ; audits et relecture en lecture seule, liens et références vérifiés ; réservations libérées |
| 2026-11-10 | ECH-033 : coordination autonome des sessions indépendantes via verrous par fichier (DEC-031) | Outil `tools/agent_lock.py` (SQLite dans `.git`), suite de tests `tests/test_agent_lock.py` (9 tests passants : concurrence 20 sessions, écritures parallèles sans perte, isolation, confinement chemins/symlinks, récupération après crash) ; AGENTS.md, README.md, DECISIONS.md et SUIVI.md mis à jour ; aucun coordinateur requis |
| 2026-11-17 | ECH-027 à ECH-031 : Livraison et validation complète du jalon MTP | Réemploi Paperasse amont (commit `e38a4e3`) sous `packages/paperasse/` ; application web Streamlit (`app.py`) multi-espaces isolés avec chat streaming OpenRouter, 6 skills, dépôt de pièces, génération de FEC et rapports ; sources publiques réelles (PCG 2026, barèmes) et API Sirene avec cache local SQLite sur serveur ; suite de tests automatisée `tests/test_mtp.py` (9 tests passants) et validation visuelle navigateurs ; prêt pour déploiement Streamlit Cloud |
| 2026-11-19 | ECH-034 : Création de l'identité de marque, charte et moteur dynamique | Plateforme (« Libérez-vous »), palette validée Noir Space Black + Blanc + Orange Ambre Solaire (`#EA580C`), touche Mac chiclet Echap rectangulaire en bas à gauche ; moteur de marque dynamique et marque blanche (`assets/brand/brand.json`, `packages/paperasse/brand.py`, `.streamlit/config.toml`, `app.py`) ; suite unitaire `tests/test_brand.py` passante (5/5) |
| 2026-11-19 | ECH-035 : Implémentation du parcours d'Onboarding initial (PAR-01) | Parcours guidé pour tout nouveau compte entreprise (`app.py`, `auth_db.py`, `agent.py`) : recherche temps réel à l'Annuaire officiel (INSEE/Sirene) ou saisie libre, qualification fiscale complète (forme juridique, TVA franchise 293 B ou réel, imposition IS/IR, date de clôture), désignation du dirigeant et IBAN de facturation, génération automatique des premières échéances fiscales en base SQLite et injection des données dans l'assistant ÉCHAP ; suite de tests `tests/test_onboarding.py` passante (3/3), total suite de tests 25/25 |
| 2026-11-19 | ECH-036 : Découplage Utilisateur ⇄ Structures et architecture multi-entités | Inscription réservée à la personne physique (Prénom, Nom, identifiant, mot de passe) sans obliger à un nom d'entreprise ; tables `entities` et `memberships` (relation N:M) avec isolation des finances, documents et conversations ; support spécifique des micro-entreprises/indépendants (dénomination automatique Nom+Prénom EI, franchise 293 B, IR) ; switcher multi-structures dans l'UI (`app.py`) permettant de gérer N structures (ex : 1 Micro + 1 SAS + 1 SCI) sur un compte unique ; suite `tests/test_onboarding.py` étendue et passante (4/4), total suite globale 30/30 |
| 2026-11-19 | ECH-037 : Alignement éditorial strict ÉCHAP (zéro emoji, épuration visuelle et fin des fuites de fichiers techniques) | Respect rigoureux de la charte de marque (sobriété radicale) : suppression totale des emojis (⏰, 🔴, 🟡, 🟢, 📋, etc.) dans les templates et l'UI au profit de mentions textuelles sobres entre crochets (`[Urgent]`, `[À prévoir]`, `[Conforme]`, `[Non configuré]`) ; suppression des séparateurs lourds pseudo-graphiques unicode (`━━━━`, `════`) ; interdiction catégorique de renvoyer l'utilisateur vers des fichiers techniques internes (`setup-facturation.md`, `company.json`, etc.) et remplacement par un guidage conversationnel direct ; salutations épurées sans déballage non sollicité de diagnostic ; suite automatisée dédiée `tests/test_prompt_tone.py` (4/4), 34/34 tests passants |
| 2026-11-19 | ECH-038 : Déploiement en ligne du MTP ÉCHAP sur GitHub et Streamlit Cloud (DEC-032) | Création et initialisation du dépôt distant public `https://github.com/nikopeya/echap` ; commit initial et push de l'application MTP Streamlit, suite de tests et assets ; configuration prête pour déploiement Streamlit Community Cloud (`app.py`, `requirements.txt`, `packages.txt`, `.streamlit/config.toml`) |
| 2026-11-19 | ECH-039 : Refonte ergonomique de l'Onboarding en parcours Typeform pas-à-pas | Remplacement du formulaire monolithique par un wizard fluide : 1 seule question affichée par écran, jauge de progression animée (25% à 100%), grandes cartes de choix cliquables avec passage automatique d'étape (Type d'activité -> Identité/SIREN -> Régime TVA -> Coordonnées & Lancement), navigation fluide Précédent/Suivant ; suite de tests unitaire 34/34 passante |
| 2026-11-20 | ECH-040 : Fiabilisation de l'inscription et accélération des reruns Streamlit | Formulaires de connexion et d'inscription atomiques (`st.form`, clés explicites, mode d'accès conservé, messages d'erreur explicites, spinner de création) : le bouton « Créer mon compte » crée réellement le compte et ouvre l'onboarding ; création/migration du schéma SQLite déplacée hors de `get_db_connection` et exécutée une seule fois par processus (verrou threading, `busy_timeout`, WAL) au lieu d'à chaque appel (≈30 requêtes DDL par connexion) ; mesure locale : connexions métier 0,5–0,8 ms/appel, connexion et inscription ≈180 ms ; nouveaux tests `tests/test_login_ui.py` (5/5), total suite 39/39 |
| 2026-11-20 | ECH-041 : Simplification du langage de l'onboarding Typeform | Remplacement du jargon administratif (« Auto-entrepreneur / Micro », « BNC », mentions d'articles de loi) par des situations du quotidien : « Je travaille à mon compte », « J'ai créé une société », « Je gère un bien immobilier », « J'exerce un métier réglementé », plus bouton refuge « Je ne sais pas encore » ; questions directes (« Sous quel nom allez-vous facturer ? », « Ajoutez-vous de la TVA sur vos factures ? ») avec explications claires et passage direct d'écran au clic ; suite complète 39/39 tests passants |
| 2026-11-23 | ECH-042 : Intégration complète Neon (PostgreSQL, Object Storage S3, Auth, Functions, AI Gateway, Realtime) | Initialisation et déploiement du projet Neon (`neon init`, `neon deploy` sur branch production). Création de l'adaptateur de persistance universel `packages/paperasse/neon_adapter.py` avec bascule automatique entre Neon Postgres (`DATABASE_URL`) et SQLite local. Migration intégrale des données existantes (20 utilisateurs, 66 entités, historique chat, documents, finances) vers Neon Postgres. Validation du build TypeScript (`npm run build`), test de bout en bout des 6 services (`test_neon_services.ts`), compatibilité `boto3` pour Object Storage S3. Suite de tests Python 39/39 passante |
| 2026-11-23 | ECH-043 : Correctif déploiement Streamlit Cloud — suppression de `packages.txt` | Le fichier ne contenait qu'une ligne de commentaire français ; Streamlit Cloud ne supporte pas les commentaires dans `packages.txt` et passait chaque mot à `apt-get install` (`E: Unable to locate package #`, `Aucune`, `dépendance`…), faisant échouer le build. Aucune dépendance système n'est requise (calculs et documents 100 % Python) : fichier supprimé. Suite de tests 39/39 passante ; accord explicite du porteur pour pousser le correctif |

Vérifications : validateur Python 3 exécuté en mémoire, contrôle `git diff --no-index --check` de chaque nouveau document, inspection de l’état Git et suite unitaire `tests/test_agent_lock.py`. La synthèse historique n’a pas été modifiée ; empreinte Git constatée : `302f9c2b7538083cebd4c05aa6457bed7a5017b6`. Aucun commit ni ajout à l’index n’a été effectué.
