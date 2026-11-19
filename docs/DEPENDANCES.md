# Dépendances et réemploi

État au 10 novembre 2026. Registre de candidats et de vérifications, pas liste de composants adoptés.

## Rôle et périmètre

ÉCHAP vise un assistant administratif professionnel complet pour la France, au-delà de la comptabilité.
Les besoins traversent comptabilité, fiscalité, facturation, devis, avoirs, documents et échéances.
Ils incluent aussi juridique d'entreprise, recouvrement, due diligence et administration des dirigeants.
Paperasse est une brique candidate à exploiter et fiabiliser, pas le produit lui-même.
Réemploi open source et audit d'abord ; aucun moteur comptable ni ledger maison n'est adopté par défaut.

Les profils du sprint 1 du MVP sont définis dans [PERIMETRE.md](PERIMETRE.md). La sélection des composants doit couvrir cette cible, et non la réduire aux seules capacités déjà présentes dans Paperasse.
L’alignement SCI exige une distinction documentation/code/tests. L’administration traitée reste celle du professionnel, pas ses dossiers métier de patients ou clients.

Le MTP précède ce MVP (DEC-026 à DEC-030) : réemploi des six skills et des connecteurs existants sur données fictives uniquement. Ses domaines privés et de copropriété n’étendent pas la cible professionnelle ; ses connecteurs sandbox/simulés n’autorisent aucune intégration de production supplémentaire en S1 MVP. La recette expérimentale est distincte des portes d’usage réel de [ROADMAP.md](ROADMAP.md).

## Méthode de sélection

1. Identifier le besoin et comparer les solutions existantes avant d'envisager du code spécifique.
2. Consigner source, version ou commit, provenance, maintenance et dépendances transitives.
3. Auditer licences, compatibilité, obligations de redistribution, données utilisées et sécurité avant réemploi ou publication.
4. Tester sur des cas français représentatifs, y compris erreurs, frontières et changements de règles.
5. Chiffrer intégration, exploitation, conformité et remplacement ; documenter risques et solution de repli.
6. Épingler la version retenue seulement après validation et suivre les mises à jour avec tests de non-régression.

La licence d'ÉCHAP et la frontière core/cloud restent à décider, malgré l'orientation open core actée.
Ne pas créer d'abstraction d'intégration prématurée : choisir d'abord selon un besoin et des preuves.
Pour le MTP, appliquer un audit proportionné aux seuls fichiers exécutés : version, droit de réemploi, dépendances nécessaires, garde-fous et smoke tests sur données fictives. La validation réglementaire exhaustive de la cible MVP n’est pas une condition de cette expérimentation ; elle le reste pour les sorties destinées à un usage réel.

## Paperasse : audit du fork et de l'amont

| Élément | État et preuve à obtenir |
| --- | --- |
| Amont | [romainsimon/paperasse](https://github.com/romainsimon/paperasse), README de master consulté le 10 novembre 2026 ; branche mobile, commit à épingler. |
| Contenu observé | Collection de skills Markdown, documentation, données, modèles et scripts ; ce n'est pas la preuve d'un moteur complet conforme. |
| Fork utilisateur | Existence déclarée par l'utilisateur ; URL toujours manquante, version, écarts à l'amont et licence effective à établir. L’audit de l’amont peut commencer sans attendre, sans le présenter comme un audit du fork. |
| Réemploi | Inventorier les fichiers réellement repris, leurs licences et obligations ; vérifier chaque dépendance transitive. |
| Comptabilité MVP | Vérifier les invariants, les écritures, les contrôles, les erreurs et la persistance avant usage réel ; pour le MTP, appliquer l’audit ciblé décrit ci-dessous. |
| FEC MVP | Le README mentionne `generate-fec.js` ; tester format, contenu et conformité sur des dossiers représentatifs avant usage réel. |
| Factur-X MVP | Vérifier l'existence, le code et les assertions du générateur, puis valider les sorties avec des outils et cas indépendants avant usage réel. |
| 2033 MVP | Le README présente un modèle de liasse en brouillon ; vérifier le code éventuel, les correspondances et les calculs. |
| SCI MVP | Les références documentaires à l'IR et à l'IS ne prouvent pas un générateur fiscal SCI codé et testé. |
| Connecteurs | Inventorier Qonto, Stripe, Pennylane et sources publiques selon version ; leur présence, leurs opérations, tests et sandboxes restent à prouver. Usage MTP fictif distinct de toute adoption en production S1 MVP. |

Les seuils, prix bancaires et commerciaux, affirmations sur signature, certification de caisse et conservation sont à vérifier.
L'affirmation d'une limite TESE à 20 salariés ne doit pas être utilisée comme règle actuelle.
La version des règles, les sources officielles et les tests applicables priment sur les assertions exploratoires.

## MTP : réemploi expérimental des six skills et connecteurs existants

Le MTP teste l'accès aux composants existants de Paperasse sur données fictives (ECH-027 à ECH-031) :
- **6 skills** : `comptable`, `fiscaliste`, `notaire`, `controleur-fiscal`, `commissaire-aux-comptes`, `syndic`.
- **Connecteurs de test** : Qonto, Stripe, Pennylane, sources publiques (sandbox ou simulation visible).
- **Principe de sélection** : exécuter l'existant avec des garde-fous stricts (paramètres bornés, isolation, aucune donnée réelle), sans redévelopper de moteurs pour ce jalon.

Les sections suivantes portent sur l'évaluation des dépendances et composants candidats pour le **MVP**.

## Comptabilité et simulations MVP : candidats, pas choix

| Candidat ou famille | Évaluation nécessaire |
| --- | --- |
| OpenConcerto | Examiner couverture comptable et fiscale française, intégration, maintenance et licence ; aucune solution ni licence supposée. |
| Bibliothèques de ledger OSS | Comparer écritures, traçabilité, corrections, clôture, exports, sécurité, licences et coût d'intégration. |
| Scripts et données Paperasse | Contrôler calculs (BigInt centimes), versions réglementaires, interfaces, tests et limites (absence de `add-entry.js`, réécriture directe de JSON plats, mono-taux TVA Factur-X). |
| Publicodes et modèles Urssaf | Évaluer `@publicodes/model-urssaf` comme simulateur de cotisations/allègements ; pas de garantie de bulletin ou de DSN. |
| legal-skills-france | Répertoire candidat pour modèles d'actes juridiques (contrats de travail, statuts, ruptures). |

Comparer les options sur des jeux de données et résultats de référence, puis documenter les écarts et arbitrages.
Aucune d'elles n'est adoptée ici ; produire un ledger maison n'est pas une décision de repli automatique.

## TESE : seule exception métier de production S1 MVP

TESE est la seule intégration métier externe autorisée en production en S1 MVP, par exception explicite, pour les mandataires éligibles. Les connecteurs fictifs MTP ne changent pas cette restriction ; l’accès TESE n’est pas un préalable au MTP.
L'éligibilité dépend de la situation de l'entreprise et du mandataire ; elle ne découle pas du seul statut de dirigeant.
La gestion d'une équipe salariée relève de S2 ; vérifier à nouveau les sources et la version métier avant cette extension.
Les sources officielles consultées sont [L'essentiel du TESE](https://www.letese.urssaf.fr/portail/accueil/s-informer-sur-offre-de-service/essentiel-du-tese.html) et sa [FAQ](https://www.letese.urssaf.fr/portail/accueil/faq.html).
Elles décrivent un portail en ligne et des limites, notamment certains cumuls mandat et contrat technique avec assurance chômage.
Depuis 2026, une entreprise peut gérer une partie de ses salariés via TESE et une autre autrement ; ne pas figer d'autres règles RH sans vérification.
Ces pages ne démontrent ni API accessible ni droit d'accès automatisé pour ÉCHAP.

Avant toute intégration, établir un accès autorisé, ses conditions, habilitations, données permises et responsabilités ; rien n'est démontré à ce jour.
Pas d’API imaginée, d’endpoint privé ni de scraping non autorisé. Sans voie d’accès démontrée, l’intégration reste bloquée ; un parcours manuel sur le portail est une solution de repli à faire arbitrer, pas une livraison équivalente.
Séparer préparation par ÉCHAP, validation utilisateur et conséquences déclaratives éventuelles du service TESE, dont les formalités liées à la DSN.
Ne pas promettre qu'ÉCHAP dépose une DSN, établit un bulletin ou prend en charge tous les cas et organismes.
Service gratuit ne veut dire ni cotisations nulles ni intégration, maintenance et contrôle gratuits.

## Frontière de production S1 MVP et candidats ultérieurs

En S1 MVP : imports locaux CSV, OFX et documents ; gestion courante et génération des déclarations pour tous les profils demandés, sans dépôt fiscal par ÉCHAP. Un utilisateur par entreprise, plusieurs testeurs avec espaces isolés selon DEC-025 ; salariés via TESE au S2 MVP.
L'exception TESE pour mandataires éligibles et ses conséquences déclaratives restent isolées de cette règle générale ; les connecteurs MTP test ne constituent pas des intégrations de production S1.
OpenRouter est le fournisseur unique envisagé pour l’inférence du MVP : infrastructure IA, non intégration métier supplémentaire ; ce n’est pas un choix imposé au MTP.
Son usage avec des données réelles est bloqué tant que minimisation, confidentialité, sous-traitants, transferts et rétention ne sont pas vérifiés.
L'anonymisation effective et le zéro rétention ne sont pas garantis par hypothèse ; valider modèle, configuration et contrat pour chaque route.

| Candidat de production après S1 MVP | Questions avant adoption |
| --- | --- |
| Agrégateur bancaire | Aucun choisi ; comparer couverture réelle des banques, consentement, sécurité, tarifs et conditions. |
| Stripe | Évaluer besoins de paiement ou de données, frais, sécurité et périmètre d'intégration. |
| Email connecté et OCR externe | Évaluer autorisations, minimisation, confidentialité, coût par volume et suppression. |
| Documenso ou autre signature | Solution auto-hébergeable candidate (audit trail SHA-256/RFC 3161) pour actes B2B (L. 110-3 C. com) ; comparer avec tiers payants qualifiés (Yousign) pour actes à fort enjeu. |
| Teledec ou concurrents fiscaux | Partenaire EDI habilité DGFiP (EDI-TDFC) ; comparer API B2B Teledec, jedeclare.com et Invoke sur accès, formats et coûts. |
| Données publiques d'entreprise | Étudier BODACC (procédures collectives, TUP/fusions), API Annuaire des Entreprises/INPI, sanctions DGCCRF et services privés d'incidents (Infogreffe, Rubypayeur, Altares). |

Ne pas supposer un palier gratuit bancaire ni un coût supérieur à 100 € pour toutes les banques.
Ne pas anticiper d'interface `BankProvider` avant besoin démontré et choix d'intégration.
Infomaniak est seulement un candidat d'hébergement ; comparer sécurité, coûts, localisation et réversibilité.
Une inférence en France et plus écologique est un objectif V2, non une capacité acquise.
Telegram est souhaité pour le produit ; son calendrier S1 reste à décider, sans préjuger d'une intégration autorisée.

## Décisions et preuves en attente

- MTP / ECH-027 : commencer l’inventaire versionné de l’amont ; obtenir l’URL et le commit du fork pour ses écarts. Vérifier licences, garde-fous et smoke tests des seuls scripts retenus, sans garantir la conformité upstream.
- MTP / ECH-028 : comparer puis faire décider base agent, harnais/runtime, stack, inférence, hébergement et coût de déploiement ; aucune installation par cette tâche documentaire.
- MTP / ECH-029 à ECH-031 : accès web et espaces isolés, connecteurs sandbox/simulés visibles, recette et retours sur données fictives uniquement.
- MVP / ECH-003 : approfondir l’audit du fork et vérifier les règles en vigueur et les cas SCI, FEC, Factur-X et 2033 avec des tests reproductibles.
- MVP : comparer les options comptables OSS avant toute décision sur le ledger.
- MVP : démontrer l’éligibilité et un accès TESE autorisé ; sinon maintenir le blocage et faire arbitrer la solution de repli.
- MVP : valider minimisation et zéro rétention effectif des routes d’inférence avant données réelles ; mesurer coût et latence.
- Tenir le registre des versions, risques, coûts et stratégies de remplacement à chaque adoption.

## Documents associés

[Accueil](../README.md) · [Vision](VISION.md) · [Périmètre](PERIMETRE.md) · [Produit](PRODUIT.md)
[Architecture](ARCHITECTURE.md) · [Sécurité](SECURITE.md) · [Économie](ECONOMIE.md)
[Décisions](DECISIONS.md) · [Roadmap](ROADMAP.md) · [Suivi](SUIVI.md)
L’adoption d’un composant reste conditionnée à ses preuves d’audit et à la décision correspondante.
