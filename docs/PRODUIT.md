# ÉCHAP — Spécification produit initiale

Statut : version de cadrage, non spécification réglementaire exhaustive. Date : 2026-11-10.

Les cibles et frontières de sprint sont définies dans [PERIMETRE.md](PERIMETRE.md). Les exigences ci-dessous sont des critères de conception et de recette à décliner en tâches ; aucune n’est déclarée implémentée.

## MTP — parcours et recette de la première enveloppe

Le MTP expose les six skills et les connecteurs existants de Paperasse selon [PERIMETRE.md](PERIMETRE.md), sur données métier fictives uniquement. Il ne doit pas attendre le développement de toute la spécification MVP des sections numérotées ci-dessous.

### Parcours MTP

1. Le testeur ouvre une page web et accède à son espace protégé, sans agent, logiciel local ni configuration de clé d’inférence.
2. Il choisit un exemple fictif ou dépose des pièces fictives ; l’interface rappelle l’interdiction des documents réels.
3. Il formule sa demande en langage naturel ; le runtime charge le skill adapté et son contexte utile sans imposer l’arborescence du dépôt au testeur.
4. Les scripts existants autorisés sont exécutés de façon contrôlée dans l’espace de test ; les contenus documentaires restent distingués des actions effectives.
5. Il consulte les réponses et les fichiers générés, peut les télécharger et signale les difficultés rencontrées.
6. Pour un connecteur, l’interface indique explicitement « sandbox », « simulé », « indisponible » ou « erreur » ; aucun état ne laisse croire à un accès de production.

### Critères d’acceptation MTP

| ID | Preuve attendue |
| --- | --- |
| MTP-01 | Un testeur sans Claude Code ni agent préalable termine un parcours depuis le navigateur, sans commande locale ni clé personnelle d’inférence |
| MTP-02 | Au moins un scénario fictif par skill, sur les six, démontre l’accès à ses ressources et un résultat consultable ; les sorties existantes sont distinguées des fonctions manquantes |
| MTP-03 | Une pièce fictive peut être déposée et un fichier produit par un script existant peut être récupéré dans le bon espace |
| MTP-04 | Chaque connecteur inventorié possède un cas sandbox ou simulé vérifié, un état explicite et un scénario d’erreur ; aucun accès ni effet métier de production |
| MTP-05 | Un testeur ne peut lire ni modifier les fichiers, conversations ou résultats d’un autre ; secrets techniques hors navigateur, prompts et logs |
| MTP-06 | Taille des fichiers, appels, durée d’exécution et dépenses sont bornés ; un échec ou arrêt conserve un état compréhensible et ne déclenche pas de boucle incontrôlée |
| MTP-07 | Les résultats portent leur caractère expérimental ; aucun audit IA n’est présenté comme une certification et aucun document comme réellement déposé ou signé |
| MTP-08 | Les testeurs peuvent donner un retour ; coût, latence et blocages sont relevés sans attendre une instrumentation ou une interface analytique complète |

Ces critères sont à implémenter et vérifier, pas des capacités déjà livrées. Ils ne requièrent ni les cinq vues, ni un nouveau ledger, ni TESE, ni une validation exhaustive des régimes fiscaux pour autoriser des essais fictifs. Les protections minimales restent celles de [SECURITE.md](SECURITE.md).

## 1. Modèle d’expérience du MVP

L’utilisateur accède à une conversation et à cinq vues de consultation. Il n’a pas à comprendre les journaux comptables, les formulaires ni l’architecture d’agents pour accomplir son travail. Il peut consulter les détails, pièces et calculs lorsqu’il le souhaite.

Au MVP, un seul utilisateur accède à chaque entreprise. Plusieurs testeurs peuvent disposer chacun d’un espace d’entreprise authentifié et isolé ; pas d’invitation, de rôle collaboratif ni d’accès partagé au dossier. Les associés et mandataires enregistrés ne sont pas automatiquement des utilisateurs. L’accès direct d’un expert-comptable est reporté après le MVP ; la revue compétente des sorties sensibles reste nécessaire.

Le chat sert à demander et expliquer ; les cartes structurées servent à vérifier et confirmer ; les vues servent à retrouver et comprendre. Une action engagée depuis une vue passe par les mêmes contrôles qu’une demande dans le chat.

Le niveau de délégation peut varier selon les actions et permissions. Toute validation sensible présente l’objet exact, les effets, les montants, le destinataire éventuel et la version concernée.

## 2. Parcours de référence

### PAR-01 — Démarrer avec la bonne qualification

1. Identifier entreprise, activité(s), forme, associés/mandataires, établissement professionnel en France et exercice.
2. Déterminer séparément les régimes fiscal, social et TVA, avec options et dates d’effet.
3. Importer les pièces existantes et demander seulement les éléments manquants indispensables.
4. Présenter le profil retenu, les obligations proposées et les points à confirmer.
5. Créer le calendrier et les dossiers selon les règles validées ; bloquer les branches non qualifiées.

Acceptation : deux entreprises de même activité mais de formes ou régimes différents n’héritent pas mécaniquement des mêmes obligations. Le profil incertain n’est pas complété par invention. L’utilisateur est authentifié et rattaché à son espace d’entreprise ; aucun second utilisateur n’est invité au MVP.

### PAR-02 — Transmettre une pièce et déléguer son traitement

1. Déposer un document local ou des données structurées ; vérifier format, taille et contenu potentiellement dangereux.
2. Préserver l’original ; détecter doublons et incohérences ; extraire des données avec leur provenance.
3. Proposer qualification et traitement applicables ; demander confirmation uniquement si nécessaire.
4. Exécuter les écritures ou mises à jour autorisées, relier pièce et opération, conserver le résultat des contrôles.

Acceptation : une donnée extraite n’est pas un fait validé ; un document contenant des instructions hostiles ne modifie pas les permissions de l’assistant.

### PAR-03 — Importer et rapprocher les flux bancaires

1. Charger un CSV/OFX compatible ; prévisualiser dates, signes, devise, solde et correspondance des colonnes.
2. Signaler les lignes rejetées et conserver une trace d’import sans données sensibles inutiles dans les logs.
3. Détecter le réimport et les recouvrements entre fichiers sans supprimer des opérations légitimement identiques.
4. Proposer rapprochements et qualifications ; distinguer mouvement bancaire, facture et écriture validée.

Acceptation : rejouer un import identifié ne double pas les opérations ; un import partiel n’est jamais affiché comme un succès complet.

### PAR-04 — Émettre et suivre une facture ou des honoraires

1. Recueillir destinataire, objet, lignes, taxes, conditions et références nécessaires.
2. Calculer en code et vérifier mentions, numérotation et règles propres au profil.
3. Prévisualiser, confirmer l’émission selon permissions, figer la version émise et générer les formats validés.
4. Suivre paiements, acomptes et avoirs ; préparer les suites comptables et relances.

Acceptation : un brouillon ne consomme pas par erreur une émission définitive ; une facture émise ne se corrige pas par écrasement. Un XML embarqué ne suffit pas à annoncer un Factur-X conforme.

### PAR-05 — Préparer une échéance ou une déclaration

1. Identifier profil, période, obligation et version des règles.
2. Collecter les données et pièces nécessaires ; afficher les manques bloquants.
3. Calculer et générer document et annexes ; exécuter les contrôles métier et de format.
4. Présenter synthèse, sources, hypothèses et résultats ; recueillir la validation requise.
5. Exporter le dossier et conserver l’historique de validation ; indiquer explicitement « non déposé ».

Acceptation : une validation ne fabrique aucun accusé de dépôt. Une modification des données après validation invalide la version à confirmer, pas l’historique existant.

### PAR-06 — Traiter un besoin administratif ou juridique

1. Identifier l’objectif : contrat, décision sociale, justificatif, formalité ou courrier.
2. Qualifier les parties, faits, dates, pouvoirs et pièces ; sélectionner une méthode applicable.
3. Générer le projet avec sources et zones à confirmer ; signaler les limites et actes réservés.
4. Lier le document au dossier et suivre les étapes restantes.

Acceptation : un projet de contrat n’est ni signé ni transmis ; une revue IA n’est ni un conseil professionnel garanti ni une certification.

### PAR-07 — Recouvrer ou vérifier une contrepartie

Préparer dossier de créance, chronologie, calculs déterministes applicables (principal, indemnité forfaitaire de 40 €, intérêts légaux BCE + 10 points) et projets de mise en demeure / requête en injonction de payer (Cerfa 12946). Structurer les données de contrepartie fournies et leur date. Exploiter l'Open Data (BODACC pour faillites et fusions/TUP avec transmission de passif, API Annuaire Entreprises/INPI, sanctions DGCCRF). Distinguer identité vérifiée, information rapportée et hypothèse.

Acceptation : pas de transfert automatique d’une dette à une entité supposée successeur sans preuve légale d'opposabilité (ex. fusion BODACC art. L. 236-3 C. com) ; pas de solvabilité certifiée sur la seule absence d’information ; pas d’envoi ni procédure externe au sprint 1.

### PAR-08 — Rémunérer un mandataire avec TESE

1. Vérifier statut et éligibilité, ainsi que l’adhésion et les autorisations d’accès.
2. Préparer les éléments nécessaires et les contrôler ; présenter les effets engageants avant confirmation.
3. Utiliser uniquement le mécanisme autorisé dont la faisabilité aura été démontrée.
4. Suivre traitement, bulletins, décomptes et preuves disponibles ; importer et comptabiliser les résultats.

Acceptation : un délai réseau n’est pas traité comme un échec certain autorisant une nouvelle déclaration ; vérifier l’état avant toute relance. Si l’accès ou l’éligibilité manque, afficher « bloqué », pas « intégré ». La production et les formalités du service restent distinctes de la préparation par ÉCHAP.

## 3. Cinq vues minimales

| Vue | Informations prioritaires | Interactions utiles |
| --- | --- | --- |
| Échéances | À faire, date, entreprise, statut, urgence, blocages | Ouvrir le dossier, fournir une pièce, confirmer une action |
| Factures | Émises/reçues, honoraires, montant, échéance, règlement, avoirs | Prévisualiser, télécharger, demander une correction ou relance |
| Documents | Originaux, type, période, rattachement, version, contrôle | Déposer, retrouver, consulter, exporter |
| Comptes et trésorerie | Soldes connus et date, flux, rapprochements, anomalies | Importer, consulter un détail et ses pièces |
| Déclarations | Obligation, période, avancement, contrôles, validation, export/dépôt réel | Ouvrir le détail, confirmer, télécharger les preuves existantes |

Pas de cockpit ERP, de menu par outil technique ni de constructeur de workflows imposé. Le contrôle d’accès s’applique aux vues, fichiers et exports autant qu’au chat.

## 4. États communs proposés

Pour les dossiers : **à qualifier → pièces manquantes / prêt à préparer → préparé → contrôlé → à confirmer → validé → exporté**. Ajouter **bloqué**, **erreur** ou **annulé** avec motif et reprise possible.

Pour une action externe autorisée, états distincts **à transmettre → transmission en cours → réception confirmée / rejetée / état inconnu**. « Déposé », « signé », « payé » exigent une preuve correspondant réellement à cet état.

Les états exacts seront spécialisés par domaine, pas imposés comme un moteur universel prématuré. Une correction crée une nouvelle version ou l’opération corrective adaptée.

## 5. Exigences transversales

| ID | Exigence | Critère de recette initial |
| --- | --- | --- |
| EX-01 | Profil et applicabilité explicites | Aucune règle fiscale choisie uniquement à partir d’un mot comme BNC ou SAS |
| EX-02 | Calculs déterministes | Résultat reproductible pour mêmes entrées et même version ; règles d’arrondi testées |
| EX-03 | Exécution contrôlée | Schéma, permission, préconditions et validation côté serveur ; le prompt ne suffit pas |
| EX-04 | Traçabilité | Relier pièce, données, règle, outil, acteur, décision et résultat sans journaliser inutilement du sensible |
| EX-05 | Historique comptable | Écritures validées non réécrites ; correction appropriée et périodes contrôlées |
| EX-06 | Confirmation ciblée | Confirmation liée à une version exacte et aux effets attendus, invalidée si le contenu change |
| EX-07 | Reprise et doublons | Imports et effets de bord rejouables sans double traitement ; état inconnu explicite |
| EX-08 | Incertitude et escalade | Pas de valeur inventée ni d’avis assuré lorsque le cas n’est pas couvert |
| EX-09 | Isolation et accès | Chaque entreprise a un seul utilisateur au MVP ; tests de refus d’accès d’un testeur aux données, fichiers, chat et exports d’une autre entreprise |
| EX-10 | Confidentialité inférence | Aucune donnée sensible envoyée sans passage des contrôles de minimisation et de rétention |
| EX-11 | Sobriété | Coût complet et latence mesurés par action ; budgets et limites définis avant ouverture |
| EX-12 | Interchangeabilité des modèles | Jeux d’évaluation métier/sécurité exécutables avant un changement de modèle |
| EX-13 | Restitution et portabilité | Export compréhensible des documents et données autorisées, sans dépendre du chat |
| EX-14 | Accessibilité | Parcours essentiels utilisables au clavier, états compréhensibles sans couleur seule, langage clair |
| EX-15 | Fraîcheur réglementaire | Règle datée avec période d’application ; source modifiée ou incertitude bloque la sortie concernée |
| EX-16 | Couverture non comptable | Recette d’au moins un parcours administratif, juridique et recouvrement, en plus des parcours comptables |

Ces critères ne définissent pas encore un niveau certifié d’accessibilité, un SLA ni une exhaustivité réglementaire. Ils doivent être déclinés en preuves et cas de test.

## 6. Catalogue initial d’actions à spécifier

Qualifier un profil ; enregistrer une pièce ; importer des mouvements ; proposer/valider une opération ; calculer une taxe ; préparer/émettre une facture ; préparer une déclaration ; générer un projet juridique ; calculer des pénalités ; préparer une relance ; assembler un dossier ; préparer/suivre un traitement TESE.

Chaque action précise : entrées typées, profil et période, droits, préconditions, règles et sources, effets, confirmation, idempotence, résultat, erreurs, audit, coût et tests. Il s’agit d’un contrat d’action, pas de noms d’API déjà adoptés.

## 7. Recette et ouverture du MVP

- Cas nominaux, limites, contre-exemples et cas non couverts pour chaque profil demandé.
- Données synthétiques au départ ; données réelles seulement après validation de la sécurité et du cadre légal applicable.
- Oracles indépendants, résultats attendus revus et tests de propriétés pour les calculs/invariants ; un LLM évaluateur ne fait pas autorité seul.
- Tests de parcours, permissions, injection, reprise, restauration et coûts ; outils de test à choisir avec la stack.
- Revue compétente des sorties comptables, fiscales et juridiques sensibles ; chaque résultat doit porter son statut de maturité.
- Les testeurs valident l’utilité et l’effort demandé ; leurs retours ne remplacent pas la validation réglementaire.

Voir [SUIVI.md](SUIVI.md) pour le travail restant et [SECURITE.md](SECURITE.md) pour les portes bloquantes.
