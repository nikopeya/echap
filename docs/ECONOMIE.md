# Économie d'ÉCHAP

État au 10 novembre 2026. Ce document distingue décisions, hypothèses et mesures manquantes.

## Proposition de valeur et clientèle

ÉCHAP vise un assistant administratif professionnel complet en France, pas seulement un logiciel comptable.
Il accompagne comptabilité, fiscalité, factures, devis, avoirs, documents et échéances.
Il couvre aussi le juridique de l'entreprise, le recouvrement, la due diligence et l'administration des dirigeants.
Paperasse est une brique candidate à exploiter et fiabiliser, non le produit ÉCHAP.
L'assistant traite l'administration propre du professionnel, pas les dossiers métier de ses patients ou clients.

Les segments du sprint 1 du MVP et leurs frontières sont définis dans [PERIMETRE.md](PERIMETRE.md), qui fait référence plutôt qu’une seconde liste économique.
Les besoins, règles et cas réellement couverts doivent être validés par segment ; une cible demandée n’est pas une garantie de prise en charge déjà complète.
Cinq à vingt testeurs ont été identifiés historiquement selon le porteur ; leur recrutement effectif et les tests réalisés ne sont pas documentés. Ce repère ne fixe pas le nombre de testeurs du MTP.
Mesurer leurs tâches, les alternatives utilisées, le temps économisé et leur disposition à payer avant de fixer l'offre.

## MTP avant MVP : vitesse et coût complet

Le MTP est une expérimentation technique sur **données fictives uniquement** (DEC-026 à DEC-030).
- **Objectif** : tester l'accès web aux 6 skills existants de Paperasse et aux connecteurs simulés/sandbox.
- **Principe de coût** : réemploi maximal, pas de développement de nouveaux moteurs. Les clés d'inférence sont portées côté serveur.
- **Budget MTP** : à arbitrer via ECH-028 (distinct du plafond MVP < 100 €/mois de DEC-021).
- Pas d'encaissement, d'abonnement ni de paiement à l'acte à implémenter pour le MTP.

Les sections suivantes portent sur le modèle économique du **MVP et de la cible commerciale**.

## Modèle commercial acté

Le modèle est freemium avec facturation à l'acte ; aucun abonnement obligatoire n'est décidé.
Une offre gratuite permet l'accès selon un périmètre et des limites encore à définir.
Des actes payants peuvent correspondre à des tâches ou traitements clairement présentés avant commande.
Les actes exacts, leurs montants, paliers, quotas et conditions commerciales restent à choisir.
Ne pas confondre coût interne d'une action, prix facturé et valeur perçue par le client.
La possibilité d'un abonnement facultatif n'est pas une décision : elle ne doit pas être supposée dans les prévisions.

L'open core est acté comme orientation ; licence d'ÉCHAP et frontière entre cœur ouvert et services cloud restent à décider.
Auditer les licences et obligations des composants réemployés avant diffusion, indépendamment du choix de licence ÉCHAP.
Un acte payant ne doit pas être exécuté sans information claire et accord sur le prix applicable.

## Enveloppe MVP et ressources

Objectif strict : infra, LLM et outils récurrents du MVP totalisent moins de 100 € par mois.
Cette enveloppe ne constitue ni une estimation mesurée ni une garantie de rentabilité.
Une machine locale puissante est disponible ; compter aussi son électricité, sa disponibilité et ses sauvegardes.
Le développement est assuré en solo avec assistance IA, notamment opencode, Hermes et d'autres outils possibles.
Le temps du fondateur, l'expertise, la conformité, les taxes et les coûts ponctuels sont suivis séparément même hors enveloppe récurrente.
Si l'enveloppe ne couvre pas une exploitation sûre, bloquer l’ouverture et faire arbitrer budget, calendrier ou périmètre par le porteur, sans supprimer les contrôles essentiels.

## Coûts à mesurer

| Poste | Unité et facteurs à relever |
| --- | --- |
| Infrastructure | Calcul local ou hébergé, électricité, réseau, disponibilité et supervision par mois. |
| Déploiement MTP | Temps d’audit ciblé, configuration de la base agent/du harnais et de l’hébergement, adaptation web et connecteurs, support et arrêt ; licences et frais ponctuels/récurrents éventuels. |
| Inférence | Requêtes, modèle, tokens d'entrée et de sortie, relances, prix appliqué et latence par action. |
| Documents | Pages OCR, traitements, taille et durée de stockage, transferts et restitution. |
| Sauvegardes | Volume, fréquence, conservation et tests de restauration, y compris copies hors site. |
| Services | Frais fixes et variables, intégration, maintenance et éventuels frais de transaction. |
| Exploitation | Support, corrections, incidents, veille réglementaire et vérifications humaines. |
| Développement | Temps du fondateur et des outils IA, conception, tests et remplacement de dépendances. |
| Conformité et taxes | Sécurité, juridique, protection des données, assurances et fiscalité propres à ÉCHAP. |

TESE peut être gratuit comme service, mais son intégration, son contrôle et son exploitation ne sont pas nécessairement gratuits.
La gratuité du service ne signifie pas que les cotisations et contributions du client sont nulles.
Les coûts de tiers et les obligations du client doivent être distingués du prix d'ÉCHAP.

## Formules de pilotage

Pour un mois donné, noter les coûts dans une même devise et sur une base HT cohérente ; suivre séparément la TVA non récupérable.
- Coût complet MTP sur sa période = coûts ponctuels de préparation/déploiement + ressources récurrentes et variables imputées à la période + temps valorisé de réalisation/support, sans double compte ; présenter aussi les seuls décaissements. Aucun plafond MTP n’est encore arrêté.
- Coût récurrent MVP = infrastructure + inférence LLM + outils récurrents ; il doit rester strictement inférieur à 100 € par mois.
- Coût d'inférence d'une action = somme, sur tous ses appels, des tokens d'entrée et de sortie multipliés par leurs tarifs unitaires respectifs, plus frais applicables.
- Coût variable d'une action = inférence + OCR + stockage et sauvegardes incrémentaux + frais tiers + part de support variable imputable.
- Coût variable d'un dossier = somme des actions et ressources imputées à ce dossier sur la période.
- Coût variable d'un tenant = somme des coûts de ses dossiers et des ressources propres au tenant sur la période.
- Recettes nettes d'un acte = prix HT encaissé moins remboursements et frais de paiement imputables.
- Marge contributive par acte = recettes nettes de l'acte moins son coût variable, sans compter deux fois les frais de paiement.
- Marge contributive mensuelle = recettes nettes mensuelles moins coûts variables mensuels, y compris ceux des utilisateurs gratuits.
- Résultat économique indicatif = marge contributive moins coûts fixes, développement, conformité et taxes pertinentes, sans double compte.

Allouer les coûts partagés selon une clé explicite et stable ; les coûts non attribuables restent dans les coûts communs.
Ne calculer moyenne par acte ou par client actif qu'avec un dénominateur non nul et une période précisée.
Suivre distribution et cas extrêmes par tenant, dossier et action, pas seulement les moyennes.
Distinguer décaissements réels et valorisation du temps du fondateur ; ne pas présenter l'indicateur comme résultat comptable certifié.
Les coûts et latences cibles chiffrés par action restent à définir après benchmark, pas à présenter comme décisions acquises.

## Maîtrise de la consommation et des risques

Pour le MTP, limiter appels, durée, pièces et dépenses, mesurer latence et coût des restitutions, et arrêter les traitements au plafond décidé. Le fournisseur d’inférence et le runtime/harnais restent ouverts jusqu’à ECH-028 ; ne pas imposer un développement custom ou une route MVP pour ce seul jalon fictif.

Pour le MVP et avant tout flux de données réelles, privilégier des workflows en code directs et déterministes ; réduire le raisonnement LLM au minimum utile.
La conception reste agnostique du modèle ; OpenRouter est le fournisseur d’accès unique envisagé pour le MVP, sous réserve du contrôle de confidentialité.
Zéro rétention effectif, minimisation, sous-traitance, transferts et paramètres de chaque route doivent être prouvés, jamais présumés ; ne pas confondre pseudonymisation et anonymisation effective.
Sans validation de ces garanties pour les données concernées, ne pas envoyer de données réelles au fournisseur.
Le routage vers un modèle plus coûteux suit une politique explicite, évaluée et plafonnée ; les engagements payants exigent l’accord approprié sans imposer une sollicitation à chaque appel interne.

Définir après mesure quotas par tenant et par action, limites de débit, taille des documents et plafond de tokens.
Un cache peut éviter des recalculs, sans partage intertenant de données sensibles et avec droits et durée de vie contrôlés.
Poser des alertes et un plafond de dépense bloquant avant les appels facturables ; prévoir la gestion des appels déjà engagés.
Au plafond ou en anomalie, arrêter les traitements coûteux, informer l'utilisateur et préserver l'accès sécurisé à ses données.
La maîtrise budgétaire ne doit pas court-circuiter isolation, sauvegardes, traçabilité ou validation humaine des actions sensibles.

## Registre économique initial

Au 10 novembre 2026 : aucune mesure économique ni benchmark n'est disponible dans ce registre.
| Mesure à collecter | État initial | Prochaine preuve |
| --- | --- | --- |
| Cadre MTP | Budget, date, durée et nombre de testeurs non arrêtés | Arbitrage porteur après comparaison ECH-028 ; aucun engagement MTP + MVP dans la semaine. |
| Coût complet MTP | Non mesuré | Estimation de déploiement ECH-028, puis temps et dépenses ECH-027 à ECH-031, tarifs datés et plafonds décidés. |
| Recrutement et usage | Non mesuré | Confirmer les testeurs, tâches et fréquence observée, séparément pour MTP et MVP. |
| Dépense mensuelle réelle | Non mesurée | Relevés infra, LLM et outils avec période et devise. |
| Coût par tenant, dossier et action | Non mesuré | Comptage des ressources, tarifs et règle d'allocation. |
| Latence et qualité | Non mesurées | Benchmarks reproductibles par tâche, modèle et jeu de cas. |
| Recettes et marges | Non mesurées | Prix décidés, actes encaissés, remboursements et coûts associés. |
| Conformité et support | Non mesurés | Temps, prestations, incidents et coûts complets. |

## Documents associés

[Accueil](../README.md) · [Vision](VISION.md) · [Périmètre](PERIMETRE.md) · [Produit](PRODUIT.md)
[Architecture](ARCHITECTURE.md) · [Sécurité](SECURITE.md) · [Dépendances](DEPENDANCES.md)
[Décisions](DECISIONS.md) · [Roadmap](ROADMAP.md) · [Suivi](SUIVI.md)
Les prix et quotas définitifs seront consignés après mesure et arbitrage.
