# Architecture d’ÉCHAP

Date : 2026-11-10. Statut : cadrage documentaire, aucune stack adoptée.
La synthèse historique est un contexte non normatif ; ses affirmations restent à vérifier.
Les décisions ci-dessous proviennent du cadrage utilisateur, pas d’une validation de cette synthèse.

## MTP avant MVP — architecture minimale

Le **Minimum Testable Product (MTP)** précède le MVP : rendre Paperasse accessible via une interface web hébergée à un testeur sans Claude Code ni installation locale.

- Réemploi des six skills Paperasse existants (`comptable`, `fiscaliste`, `notaire`, `controleur-fiscal`, `commissaire-aux-comptes`, `syndic`).
- Connecteurs (Qonto, Stripe, Pennylane, sources publiques) en sandbox ou en simulation sur données fictives.
- Isolation par espace/testeur avec wrappers contrôlés côté serveur. Aucun shell, SQL arbitraire ou réseau libre exposé au LLM.
- Stack et hébergement libres pour ce jalon : privilégier la rapidité de mise en œuvre et le réemploi.
- Données métier fictives exclusivement.

Les sections suivantes cadrent l'architecture cible du **MVP et sa suite**.

## 1. Décisions utilisateur

- ÉCHAP est un assistant administratif professionnel pour la France, pas un ERP.
- Il couvre comptabilité, fiscalité, facturation, juridique d’entreprise, recouvrement, obligations, documents et due diligence.
- Le MVP conserve la cible professionnelle large du périmètre, la gestion courante et la génération des déclarations applicables, sans dépôt fiscal S1.
- L’expérience associe conversation et visualisation ultra minimale.
- Simplicité, élégance, efficience, coût et latence sont des contraintes de conception.
- Au MVP, le harnais d’orchestration doit être custom et minimal ; aucune autonomie générale n’est recherchée.
- Calculs et actions métier sont déterministes, testés et exécutés hors LLM.
- Le LLM n’a aucun accès direct à la base, au shell ou à un réseau libre.
- Les règles sont versionnées ; les décisions et actions sont traçables.
- Au MVP, l’inférence passe par un seul fournisseur à un instant donné ; OpenRouter est envisagé sous conditions de confidentialité.
- Le modèle reste substituable ; le raisonnement renforcé est exceptionnel et borné.
- Le budget mensuel MVP infrastructure, LLM et outils doit rester inférieur à 100 €.
- Le développement local sur une machine puissante est privilégié pour le MVP ; 5 à 20 testeurs sont identifiés.
- Au MVP, un utilisateur par entreprise ; plusieurs espaces d’entreprise authentifiés et isolés. Les accès partagés et rôles collaboratifs viennent après le MVP (DEC-025).
- Paperasse est une brique à examiner et fiabiliser, pas le produit ; le fork déclaré disponible reste à identifier et versionner.

## 2. Hypothèses et arbitrages non résolus

- Aucun code applicatif, package installé ou choix de stack n’est établi à cette date.
- Un monolithe modulaire est proposé ; les microservices et le scaffolding inutile sont écartés du cadrage.
- Le web chat est le canal S1 proposé, sans décision technique de framework.
- Telegram est un canal souhaité ; son calendrier reste à arbitrer, sans report acté.
- L’hébergement reste indécis ; Infomaniak est une piste, sans immunité juridictionnelle présumée.
- L’inférence V2 dans des datacenters français écologiques est un objectif à concilier avec la confidentialité.
- Le réemploi OSS est à étudier avant un ledger maison ; aucun des deux n’est arbitré.
- Le choix PostgreSQL ou SQLite, ainsi que l’organisation ledger/base de lecture, reste ouvert.

## 3. Proposition de découpage minimal

- Une interface de conversation expose aussi les pièces, montants et validations nécessaires.
- Une couche applicative authentifie, autorise et porte le contexte d’organisation.
- Un harnais sélectionne un petit ensemble d’outils typés selon la tâche autorisée.
- Une passerelle d’inférence centralise minimisation, limites, routage et métriques.
- Des modules métier indépendants du LLM calculent, contrôlent et produisent les documents.
- Un stockage transactionnel conserve les états métier et les validations.
- Un espace de pièces séparé applique les mêmes droits et politiques de conservation.
- Un journal d’audit dédié trace les événements utiles sans recopier les conversations intégrales.
- Des traitements différés bornés gèrent imports et maintenance, sans imposer une infrastructure distribuée.
- Les frontières sont logiques dans un déploiement simple, non des services réseau obligatoires.

## 4. Parcours d’une demande et contrôles

1. Le serveur vérifie l’identité, son rattachement autorisé à l’entreprise et l’autorisation sur chaque objet et action.
2. Il classe la tâche, sa sensibilité, son risque et son budget maximal.
3. Il prépare le contexte strictement nécessaire ; les documents restent des données non fiables.
4. La passerelle n’envoie le contexte qu’après contrôle de conformité de la route d’inférence.
5. Le modèle peut proposer un appel d’outil structuré, jamais exécuter une instruction arbitraire.
6. Le serveur valide schéma, droits, préconditions et cohérence métier indépendamment du modèle.
7. Un aperçu rend visibles effets, pièces utilisées, hypothèses et règles applicables.
8. Une confirmation proportionnée au risque précède la mutation ou l’engagement externe.
9. L’exécuteur revalide l’état, applique la transaction et conserve un résultat traçable.
10. Une reprise après interruption vérifie le résultat avant toute nouvelle tentative.

## 5. Données, calculs et ledger

- Séparer organisations, utilisateurs, mandats, pièces, brouillons, écritures validées et événements d’audit ; au MVP un seul utilisateur est rattaché à chaque entreprise.
- Les brouillons restent modifiables ; seules les écritures validées relèvent du principe append-only.
- Une correction validée passe par une opération explicite liée à l’original, pas une réécriture silencieuse.
- Les transactions garantissent équilibre, unicité, séquences et absence de validation partielle.
- Prévoir clés d’idempotence et contrôles de concurrence sur toutes les mutations sensibles.
- Les vues de lecture éventuelles doivent être reconstructibles et rapprochées du registre de référence.
- Le stockage en centimes ne résout pas tous les arrondis : taux, prorata, devise et ordre des opérations sont spécifiés.
- Les règles d’arrondi et leurs cas limites sont testés sur des exemples de référence validés.
- Une empreinte peut détecter une altération ; elle ne prouve ni conformité comptable ni valeur probante suffisante.
- Les exports comptables et documents réglementés exigent validation de format et revue métier avant revendication de conformité.

## 6. Règles, recherche et qualité

- La recherche réglementaire est préparée et maintenue hors des conversations usuelles.
- Chaque règle porte source, périmètre, dates d’effet, version, validation et conditions d’invalidation.
- La veille suit le risque et les événements normatifs ; aucun délai universel de six mois ne garantit la fraîcheur.
- Une règle périmée ou douteuse est désactivée ou soumise à revue selon son risque ; le calcul concerné peut être bloqué.
- Une sortie permet de retrouver données retenues, version de règle, contrôles et auteur de la validation.
- Paperasse et tout autre OSS nécessitent examen de licence, maintenance, tests et exactitude avant réemploi.
- Les évaluations couvrent exactitude métier, abstention, injections, autorisations, coût et latence.
- Un agent critique peut contribuer aux évaluations ; il ne constitue ni preuve ni assurance contre l’erreur.

## 7. Périmètre des interfaces S1

- Les imports locaux CSV, OFX et documents sont prévus ; ils passent par validation et détection des doublons.
- Aucun contrat BankProvider anticipé n’est nécessaire pour ces imports.
- TESE est la seule intégration métier externe prévue en S1, pour les mandataires éligibles.
- Son accès autorisé, ses modalités techniques et une éventuelle API ne sont pas prouvés.
- Aucun développement ne doit présumer une API TESE ni contourner l’accès par scraping.
- À défaut de faisabilité démontrée, exposer le blocage et arbitrer le périmètre, sans faux succès d’intégration.
- Aucune paie maison ; TESE pour les salariés relève de S2, sous vérification d’éligibilité.
- Banque, Stripe, e-mail/OCR connecté, signature Documenso et dépôts fiscaux viennent après S1.
- Les fonctions de due diligence S1 n’impliquent donc pas de nouveau connecteur métier externe.

## 8. Note décisionnelle stack — une page

Objectif MVP : choisir le minimum soutenable pour le produit, pas maximiser le nombre de technologies.
Toutes les bibliothèques et solutions évoquées restent candidates ; aucune n’est réputée disponible. Pour le MTP, la comparaison commence par le runtime et les SDK existants avant toute préférence de stack MVP.

| Option | Atouts à vérifier | Coûts et risques | Critère de choix |
| --- | --- | --- | --- |
| TS-first | Types partagés interface/serveur, un langage principal, contrats d’outils cohérents | Discipline nécessaire pour décimaux, fichiers et validation à l’exécution | Option recommandée pour un S1 minimal |
| TS + Python ciblé | Conserve une base TS et réemploie un moteur Python réellement utile | Deux environnements, sérialisation, packaging et tests de frontière | Un gain mesuré justifie un composant isolé |
| Python-first | Pertinent si des moteurs documentaires ou métier éprouvés dominent le besoin | Interface web et contrats interlangages peuvent accroître le travail | Une preuve de réemploi et de coût total inverse la préférence |

Recommandation : TS-first, sans adoption à ce stade ; Python uniquement pour un besoin démontré.
Comparer un parcours complet sur exactitude, latence, mémoire, exploitation et effort de maintenance.
Évaluer d’abord les composants OSS existants ; ne pas déduire de ce choix un ledger maison.
Choisir PostgreSQL ou SQLite après essais de concurrence, isolation, sauvegarde et restauration.
Consigner décision, alternatives rejetées et critères mesurés dans [DECISIONS.md](DECISIONS.md).

## 9. Budgets, confidentialité et conditions de livraison

- Mesurer latence médiane/haute, coût par tâche et coût mensuel projeté sur les volumes bêta.
- Limiter taille des pièces, contexte, appels, durée et dépenses ; interrompre proprement au plafond.
- Le raisonnement renforcé exige un gain d’évaluation par tâche, un plafond et le même provider actif.
- Les caches restent cloisonnés par organisation et compatibles avec la sensibilité des données.
- Démontrer le zéro rétention contractuellement et techniquement pour chaque route effective du MVP, y compris les replis, avant tout flux sensible réel.
- Bloquer les flux sensibles non conformes ; pseudonymisation et anonymisation ne sont pas interchangeables.
- Aucune ouverture avec données réelles ne contourne les conditions bloquantes de [SECURITE.md](SECURITE.md) pour tenir une date ; le MTP applique ses propres conditions proportionnées.

## 10. Références et limites du document

Le cadrage produit relève de [VISION.md](VISION.md), [PERIMETRE.md](PERIMETRE.md) et [PRODUIT.md](PRODUIT.md).
Les coûts et composants seront détaillés dans [ECONOMIE.md](ECONOMIE.md) et [DEPENDANCES.md](DEPENDANCES.md).
Le pilotage relève de [ROADMAP.md](ROADMAP.md), [SUIVI.md](SUIVI.md) et du [README](../README.md).
Les décisions techniques définitives et leurs preuves restent à enregistrer avant implémentation.
