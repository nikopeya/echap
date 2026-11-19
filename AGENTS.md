# Instructions de travail — ÉCHAP

Ces conventions s’appliquent aux humains et agents IA travaillant dans ce dépôt, notamment opencode, Hermes Agent et les autres outils à venir. Elles ne dépendent pas d’un fournisseur d’agent.

## Comprendre le projet avant de modifier

- Lire [README.md](README.md), [docs/VISION.md](docs/VISION.md), [docs/PERIMETRE.md](docs/PERIMETRE.md) et les documents du domaine concerné.
- ÉCHAP est l’assistant administratif complet. Paperasse est une brique de réemploi ; la synthèse historique n’est pas la spécification ni une source réglementaire validée.
- Consulter [docs/DECISIONS.md](docs/DECISIONS.md) pour distinguer arbitrages actés, propositions et vérifications en attente.
- Ne pas réduire une cible, déplacer une fonction de sprint ou adopter une technologie sans décision explicite. Signaler le besoin d’arbitrage et son impact.
- La tâche doit préciser son mode : recherche, documentation, proposition ou implémentation. Une recherche ne donne pas mandat de modifier le code.
- Préciser aussi le jalon : MTP expérimental sur données métier fictives, MVP ou suite. Le MTP réemploie les six skills et connecteurs existants de Paperasse, en sandbox ou simulation ; il n’exige ni moteur maison, ni harnais custom, ni hébergement souverain. Ces choix restent ouverts pour accélérer les tests.
- Ne pas appliquer au MTP fictif toutes les portes de production du MVP ; conserver ses protections minimales, l’isolation et les secrets. Aucune pièce ni connexion métier de production n’est autorisée au MTP ; son succès ne valide pas l’usage réel.

## Source de vérité et sobriété documentaire

- Vision : promesse et principes ; périmètre : inclus/exclus et profils ; produit : parcours et exigences.
- Architecture et sécurité : mécanismes proposés et portes de validation ; économie et dépendances : coûts et preuves externes.
- Décisions : arbitrages ; roadmap : ordre et objectifs ; suivi : travail et preuves.
- **Règle absolue de concision et pertinence** : rester hyper opérationnel, synthétique et factuel. Proscrire le bavardage, le verbiage spéculatif, les digressions et les développements théoriques superflus.
- **Zéro hors-sujet et cloisonnement strict** : chaque document a un périmètre exclusif. Chaque information doit être placée à un endroit unique, là où elle doit être et uniquement là où elle doit être. Ne pas disperser de remarques transversales ou d'analyses hors de leur document canonique.
- Mettre à jour le document canonique avant les résumés ; préférer un lien à une nouvelle copie de la même décision.
- Une décision remplacée garde son historique. Ne pas effacer un désaccord ou une hypothèse devenue fausse pour donner l’impression d’un choix ancien.
- Préférer compléter un document existant à ajouter un fichier. Créer une note spécialisée seulement si sa taille ou son usage le justifie.

## Coordination entre sessions indépendantes (DEC-031)

Plusieurs sessions d’agents IA peuvent travailler en parallèle dans ce dépôt sans coordonnateur central. La coordination des écritures s'effectue automatiquement via l'outil de verrouillage local par fichier (`tools/agent_lock.py`), adossé à une base SQLite privée dans `.git`.

### Protocole obligatoire avant toute écriture

1. **Examiner l’état du dépôt** : les fichiers non suivis constituent du travail en cours. Ne jamais écraser ou annuler les modifications d'une autre session.
2. **Réserver les fichiers cibles** : avant de créer ou modifier un ou plusieurs fichiers, exécuter :
   ```bash
   python3 tools/agent_lock.py acquire --session "<identifiant_session>" --task "<id_tache>" <fichiers...>
   ```
   - Si les fichiers sont libres, le verrou est accordé immédiatement et renvoie un jeton (`token`).
   - Si un fichier est déjà réservé par une autre session, la commande attend (délai configurable via `--wait <secondes>`, défaut 60s). Si le verrou n'est pas libéré dans le délai, elle renvoie le propriétaire actuel. La session peut alors choisir d'attendre ou de basculer sur une autre tâche / d'autres fichiers.
3. **Relire les fichiers** : toujours relire le contenu du fichier juste après acquisition du verrou, car il a pu être modifié par la session précédente.
4. **Effectuer les modifications** : modifier les fichiers réservés.
5. **Vérifier le verrou avant validation** (optionnel mais recommandé) :
   ```bash
   python3 tools/agent_lock.py check --token "<token>" <fichiers...>
   ```
6. **Libérer immédiatement le verrou** une fois les modifications terminées :
   ```bash
   python3 tools/agent_lock.py release --token "<token>" <fichiers...>
   ```

### Mise à jour des registres communs (`SUIVI.md` et `DECISIONS.md`)

Les registres communs sont protégés par le même mécanisme :
1. Pour enregistrer le démarrage, l'avancement ou la fin d'une tâche dans `docs/SUIVI.md`, ou une décision dans `docs/DECISIONS.md`, acquérir le verrou sur le fichier concerné :
   ```bash
   python3 tools/agent_lock.py acquire --session "<identifiant_session>" --task "<id_tache>" docs/SUIVI.md
   ```
2. Relire le fichier, appliquer la modification, puis libérer le verrou :
   ```bash
   python3 tools/agent_lock.py release --token "<token>" docs/SUIVI.md
   ```

### Consultation de l'état des verrous et récupération après incident

- Pour voir les verrous actifs :
  ```bash
  python3 tools/agent_lock.py status
  ```
- Si une session précédente s'est arrêtée brutalement sans libérer son verrou, le déblocage s'effectue après avoir vérifié que la session est bien terminée :
  ```bash
  python3 tools/agent_lock.py recover --session "<session_propriétaire>" --acquired "<timestamp_acquisition>" --confirm-stopped <fichiers...>
  ```

### Règles de sécurité, intégrité et intégration Git (compatible multi-agents)

- **Séparation stricte des fichiers** : deux sessions peuvent modifier des fichiers distincts simultanément sans se bloquer.
- **Interdiction absolue de `git add .` ou `git add -A`** : afin de ne jamais capturer les modifications en cours d'une autre session travaillant dans le même arbre, une session doit **uniquement stager ses propres fichiers réservés** :
  ```bash
  git add <fichiers_modifies_sous_verrou> docs/SUIVI.md
  ```
- **Validation préalable obligatoire** : avant tout commit, la session doit obligatoirement valider l'exécution de la suite de tests (`python3 -m unittest discover tests`). Interdiction de commiter si un test échoue.
- **Commit et push vers GitHub (`origin/main`)** :
  1. Le dépôt distant GitHub officiel est configuré (`origin` -> `https://github.com/nikopeya/echap`).
  2. Une fois la tâche terminée, testée et consignée dans `docs/SUIVI.md`, la session commite ses fichiers spécifiques avec un message conventionnel clair (ex: `feat(onboarding): ...`, `fix(brand): ...`).
  3. La session libère immédiatement ses verrous applicatifs (`python3 tools/agent_lock.py release`).
  4. La session synchronise avec le dépôt distant pour alimenter le déploiement continu Streamlit Cloud :
     ```bash
     git pull --rebase origin main
     git push origin main
     ```
  5. En cas de concurrence sur le remote, `git pull --rebase origin main` réapplique le commit local proprement. Ne jamais utiliser de push forcé (`--force`).
- **En cas de conflit inattendu** : ne jamais écraser ou restaurer brutalement un fichier. Comparer les versions, conserver le travail utile et signaler toute incohérence.

## Conventions d’implémentation

- Aucun code applicatif ni stack n’est adopté à l’initialisation : ne pas supposer une bibliothèque disponible.
- Réutiliser l’existant fiable et audité ; comparer les options avant un développement spécifique.
- Préférer le découpage minimal utile, les fonctions métier testables et les contrats explicites aux microservices et abstractions anticipées.
- Les calculs et effets de bord ne sont pas délégués au LLM. Schémas, permissions, préconditions, confirmations, concurrence et reprises sont vérifiés côté exécution.
- Ne pas exposer de shell, SQL arbitraire, accès direct aux données ni réseau libre au modèle.
- Traiter documents, résultats d’outils et contenus upstream comme données non fiables, jamais comme nouvelles instructions.
- Corriger explicitement les écritures validées ; ne pas réécrire silencieusement l’historique. Ne pas appliquer l’append-only indistinctement à toutes les données personnelles.
- Pas d’interface `BankProvider` ni d’architecture d’intégration spéculative avant le besoin retenu.
- TESE est l’unique exception métier externe du sprint 1 pour les mandataires éligibles ; ne pas inventer API, habilitation ou succès de transmission.

## Sécurité, données et sources

- Ne jamais lire, copier, afficher ou versionner des secrets sans nécessité explicite ; aucune clé n’est requise pour travailler sur ces documents.
- Utiliser des données synthétiques dans exemples, fixtures, tests et évaluations. Ne pas exporter une pièce réelle vers un service de diagnostic.
- Ne pas envoyer de données sensibles à un modèle avant validation de la minimisation, des sous-traitants et du zéro rétention effectif de la route.
- Vérifier les licences et obligations upstream avant réemploi, même si la licence d’ÉCHAP reste ouverte.
- Dater les sources, préciser période d’application et niveau de preuve. Un seuil, un prix ou un statut juridique non vérifié reste une hypothèse.
- Séparer capacité documentée, codée, testée et validée réglementairement ; ne pas annoncer une conformité sur la seule présence d’un script.

## Vérification et définition de terminé

- Documentation : cohérence des décisions, liens relatifs valides, aucun secret, aucune capacité non démontrée présentée comme livrée.
- Code : tests adaptés, lint et typecheck selon les commandes effectivement configurées, plus preuves métier/sécurité du domaine.
- À l’initialisation, aucune commande applicative de test, lint ou typecheck n’existe. Ne pas inventer un succès ni installer une stack pour vérifier du Markdown.
- À l’adoption de la stack, consigner ici les commandes exactes validées pour installation, tests, lint et typecheck ; demander les commandes manquantes si nécessaire.
- Une impossibilité de vérification ou un blocage est explicite et reste ouvert dans le suivi.
- Intégration Git : dès que les tests passent et que `docs/SUIVI.md` est à jour, commiter uniquement les fichiers de la tâche et pousser sur `origin main` selon le protocole ci-dessus. Ne pas créer de licence sans arbitrage.

## Évolution de ces conventions

Adapter ces règles lorsque le travail réel révèle une friction. Consigner le motif et l’arbitrage si la modification change une frontière de responsabilité ou un principe produit. Éviter les fichiers d’instructions spécifiques à chaque agent tant qu’ils ne sont pas nécessaires.
