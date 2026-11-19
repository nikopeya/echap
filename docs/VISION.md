# ÉCHAP — Vision et principes

Statut : cadrage fondateur. Date : 2026-11-10.

## 1. Promesse

Libérer l’entrepreneur du travail administratif, comptable, fiscal, réglementaire et juridique lié à son activité, avec un assistant accessible qui demande le minimum d’effort et rend visibles les seuls éléments utiles.

L’ambition est de remplacer : 
- l’empilement de logiciels 
- la majorité du travail de gestion et administratif de l'entrepreneur et de ses collaborateurs
- la majorité du travail aujourdhui confié à un expert-comptable, sans revendiquer les titres ni actes réservés aux professions réglementées.

ÉCHAP est le produit. Des dépôts, solutions et intégrations open source ou propriétaires sont des moyens d’accélérer sa construction. 


## 2. Expérience recherchée

- L’utilisateur explique un besoin, transmet une pièce ou consulte une information ; il ne pilote pas une chaîne d’outils.
- L’assistant connaît le contexte de l’entreprise, les obligations applicables et les travaux déjà réalisés.
- Il collecte seulement les informations manquantes qui ne peuvent être obtenues de manière fiable autrement.
- Il exécute les opérations encadrées, détecte les incohérences et présente les validations réellement nécessaires.
- Il rend compte de ce qui est préparé, validé, transmis ou encore bloqué, sans confondre ces états.
- Il s'adapte au niveau de connaissance et d'expertise de son interlocuteur, lui permet de prendre des décisions éclairées, et évite tout verbiage inutile.
- Il reste strictement limité à son domaine d'utilisation et refuse toute discussion ou tâche tierce. 
- Une visualisation légère permet de voir les échéances, factures, documents, trésorerie et déclarations ; le chat n’est pas l’unique moyen de retrouver une preuve ou de confirmer un document.

Canaux souhaités à terme : Web, Whatsapp, Telegram, appli mobile. 

## 3. Problèmes à résoudre

| Problème utilisateur | Réponse recherchée |
| --- | --- |
| Informations et justificatifs dispersés | Contexte unifié de l’entreprise et documents reliés aux opérations |
| Temps passé et travail permanent| Élimination ou réduction au maximum du travail du dirigeant |
| Méconnaissance des règles comptables et légales | Guidage complet et confiance |
| Méconnaissance des procédures | Garantie de conformité, procédures automatisées ou guidées |
| Coût d'un expert comptable | Éliminer l'expert comptable partout où c'est possible |
| Peur de rater une obligation | Échéances personnalisées, suivi des pièces manquantes et des actions |
| Double saisie et complexité des logiciels | Import, extraction assistée et actions métier directes |
| Règles et calculs complexes | Règles sourcées, calculs reproductibles et limites explicites |
| Incertitude sur l’état d’un dossier | Statuts lisibles et preuves consultables |
| Prix des outils et prestations | Freemium et actes facturés de manière compréhensible |
| Données d’entreprise confidentielles | Minimisation, contrôle d’accès et inférence sous conditions strictes |
| Absence d'optimisation fiscale et comptable | Optimisation permettant des économies |

Ces problèmes sont pour l'instant des hypothèses produit pas encore testées.

## 4. Principes non négociables

### Simplicité à tous les niveaux

L’interface, le code et l’exploitation doivent rester sobres. Réutiliser une brique existante si elle est adaptée et fiable ; ne pas multiplier frameworks, services ou abstractions pour anticiper un futur hypothétique. Le temps gagné par l’utilisateur ne doit pas être remplacé par du paramétrage.

### Déterminisme des actions, incertitude explicite de l’interprétation

Le LLM ne tient pas le rôle d’un moteur de calcul ni d’un arbitre réglementaire autonome, mais uniquement d'une interface et d'un conseiller lorsque c'est nécessaire. Les calculs, validations, transitions et effets de bord passent par des outils déterministes. La qualification d’un document ou d’une situation peut rester incertaine : elle doit alors être confirmée ou bloquée.

Un prompt strict, un second agent ou une chaîne de hachage ne constituent pas à eux seuls une preuve de conformité. L’objectif de fiabilité maximale n’est pas une promesse crédible de zéro erreur absolu.

Le travail et la réflexion du LLM doivent être minimisées par l'architecture afin de maintenir une latence très faible pour l'utilisateur et un coût en token réduit. 

### Sécurité et conformité avant calendrier

L’objectif initial est un sprint d’une semaine. Une fonction ne devient pas exploitable avec des données réelles parce que le délai expire. Les fonctions non vérifiées restent bloquées ou en démonstration clairement identifiée ; le périmètre demandé demeure visible dans le suivi.

### Délégation réelle, confirmations proportionnées

Automatiser la préparation et les actions réversibles dans les permissions accordées. Réserver les confirmations aux décisions engageantes, ambiguïtés et sorties sensibles. Ne pas faire valider chaque micro-étape pour déplacer le travail vers l’utilisateur.

### Coûts et vitesse dès la conception

Préparer les méthodes et connaissances en amont. Charger seulement le contexte utile, traiter les calculs en code et limiter les tours d’inférence. Le raisonnement approfondi et la recherche web sont exceptionnels, justifiés et bornés. Mesurer coût, latence et qualité par parcours.

### Confidentialité vérifiable

Minimiser et dépersonnaliser systématiquement les données envoyées au modèle ; ne pas appeler anonymisation une simple pseudonymisation. Pour le MVP et avant tout flux sensible réel, exiger zéro rétention sur les routes d’inférence concernées et démontrer la configuration et les engagements applicables. Ne pas envoyer de données sensibles si les conditions ne sont pas satisfaites. Les scénarios métier strictement fictifs du MTP ne sont pas bloqués par cette preuve préalable ; les secrets et données d’accès des testeurs restent protégés.

Aucun hébergement n’offre une immunité générale face aux autorités. La promesse est la protection et la maîtrise des données, pas leur soustraction aux obligations légales.

### Flexibilité et réversibilité

Les modèles évoluent rapidement : pouvoir en changer sans réécrire le métier. Les composants doivent être remplaçables à un coût raisonnable, sans construire une architecture générique avant le besoin. Les décisions sont datées, motivées et remplaçables.

## 5. Positionnement

- Utilisateurs et activités professionnellement établis en France.
- Self-service ; la répartition réelle des responsabilités et le périmètre des actes réglementés sont à faire examiner, pas à régler par une mention de non-responsabilité.
- Option de revue, attestation ou intervention d’un expert-comptable partenaire selon le besoin, par exemple une demande bancaire. L’accès direct du partenaire à l’espace de l’entreprise est envisagé après le MVP, selon DEC-025. Ne pas confondre cette prestation avec la certification légale des comptes par un commissaire aux comptes.
- Administration de l’activité des professions réglementées, pas réalisation de leurs actes métier ni gestion de leurs dossiers patients/clients.
- Produit open core, avec licence et séparation cœur/offre opérée encore ouvertes.

## 6. Ce qu’ÉCHAP ne doit pas devenir

- Un ERP complexe ou un chatbot qui répond sans réaliser le travail.
- Un agent disposant librement du shell, des données et des portails administratifs.
- Un assemblage de prompts présenté comme un moteur fiscal validé.
- Un produit limité à la comptabilité par facilité technique.
- Une interface supposée certifier, signer, déposer ou encaisser alors qu’elle a seulement préparé un document.

## 7. Indicateurs de réussite à instrumenter

Temps et sollicitations utilisateur par dossier ; couverture des obligations applicables ; erreurs détectées avant sortie ; taux de blocage justifié ; qualité des justificatifs et de l’audit ; coût complet par action/dossier ; latence ; adoption et retours des testeurs.

Les cibles chiffrées restent à définir après les premiers benchmarks. Voir [PRODUIT.md](PRODUIT.md), [ECONOMIE.md](ECONOMIE.md) et [SECURITE.md](SECURITE.md).
