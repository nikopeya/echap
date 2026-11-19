# Sécurité et conformité d’ÉCHAP

Date : 2026-11-10. Statut : exigences de cadrage, garanties non encore démontrées.
La synthèse historique n’est pas une source normative ; aucune de ses assertions ne vaut validation.
Ce document distingue décisions utilisateur, hypothèses à qualifier et mesures proposées.

## MTP avant MVP — sécurité proportionnée aux tests fictifs

Le **Minimum Testable Product (MTP)** applique une sécurité adaptée à des tests sur données fictives :

- **Données métier fictives exclusivement** : interdiction stricte de charger des pièces ou données réelles d'entreprises.
- **Isolation et secrets** : espaces testeurs séparés, secrets d'API conservés côté serveur, HTTPS obligatoire.
- **Exécution contrôlée** : wrappers de scripts stricts, pas de shell libre, de SQL arbitraire ni d'accès réseau non contrôlé pour le modèle.
- **Connecteurs** : uniquement en sandbox fictive ou simulation explicitement signalée.
- Les contraintes de zéro rétention contractuelle certifiée et de conformité réglementaire exhaustive s'appliquent au MVP réel, pas au MTP fictif.

Les sections suivantes définissent le cadre de sécurité et de conformité du **MVP**.

## 1. Décisions utilisateur et limites de garantie

- La confidentialité, la simplicité et la maîtrise des coûts sont requises dès la conception.
- Le LLM n’accède directement ni à la base, ni au shell, ni à un réseau libre.
- Calculs et actions sont déterministes, testés hors LLM et soumis aux contrôles applicatifs.
- Les confirmations sont proportionnées au risque ; la traçabilité et le versionnage sont obligatoires.
- Au MVP, l’inférence utilise un seul fournisseur à un instant donné ; OpenRouter est envisagé sous conditions de confidentialité.
- Minimisation et anonymisation sont systématiquement recherchées avant transmission.
- Pour le MVP et avant tout flux sensible réel, le zéro rétention doit être démontré contractuellement et techniquement, route par route.
- Les flux sensibles non conformes sont bloqués, sans dérogation de calendrier.
- Aucune promesse de zéro erreur, de conformité automatique ou de protection assurantielle par agent critique.

## 2. Hypothèses et qualifications ouvertes

- Aucun hébergeur, stockage, mécanisme d’authentification ou package de sécurité n’est adopté.
- Infomaniak est une piste, sans immunité face aux lois, accès ou transferts applicables.
- Une inférence V2 en France dans des datacenters écologiques reste un objectif, pas une garantie actuelle.
- Qualifier les rôles RGPD d’ÉCHAP, des clients et des sous-traitants selon chaque traitement.
- Établir finalités, bases légales, destinataires, contrats et nécessité éventuelle d’une AIPD.
- L’accès TESE autorisé et l’éligibilité des mandataires S1 restent à prouver.
- Les qualifications juridiques demandent une revue compétente ; ce document ne les tranche pas.

## 3. Menaces prioritaires

| Menace | Conséquence | Mesure proposée et preuve attendue |
| --- | --- | --- |
| Accès entre organisations | Divulgation ou modification de pièces et écritures | Isolation serveur et tests croisés sur chaque famille d’objets |
| Accès objet ou action non autorisé | Lecture, export ou validation non autorisés | Autorisation objet/action et tests négatifs |
| Injection dans document ou résultat d’outil | Exfiltration, détournement d’action | Données non fiables, outils bornés et scénarios adversariaux |
| Compte, session ou clé compromis | Usurpation et dépenses abusives | Révocation, limitation et alertes testées |
| Import hostile | Exploitation du parseur, déni de service | Quotas, isolation et corpus malveillant |
| Règle fausse ou périmée | Erreur fiscale, juridique ou comptable | Versions, veille, désactivation et revue métier |
| Perte ou corruption du stockage | Indisponibilité et perte de preuve | Sauvegardes isolées et restauration testée |
| Fournisseur ou sous-traitant non conforme | Rétention ou transfert non autorisé | Dossier de route vérifié et blocage par défaut |

## 4. Identités, organisations et accès objets

- Toute requête porte une identité serveur et une organisation autorisée ; le modèle ne choisit pas son tenant.
- Vérifier les droits sur lecture, recherche, téléchargement, export, mutation et tâches différées.
- Un identifiant imprévisible ou une URL signée ne remplace jamais l’autorisation sur l’objet.
- Cloisonner également index, caches, pièces, historiques, journaux et résultats d’outils.
- Au MVP, un seul utilisateur par entreprise ; invitations, rôles collaboratifs et accès partenaire direct après le MVP. L’authentification et l’isolation entre entreprises restent requises.
- Distinguer préparation et validation selon le risque métier, même lorsqu’une même personne les réalise ; les confirmations restent obligatoires lorsque l’action l’exige.
- Les mandats ont un périmètre, une durée, une preuve et une révocation vérifiable.
- Protéger les sessions contre fixation, vol, rejeu et requêtes intersites ; renforcer les opérations sensibles.
- Prévoir authentification renforcée, récupération sûre et révocation des sessions après compromission.
- Les accès support ou administration sont exceptionnels, limités et audités ; aucun accès implicite global.

## 5. Frontière LLM, documents et outils

- Les pièces, messages importés et réponses d’outils ne constituent jamais des instructions de confiance.
- Séparer instructions système, données citées et sorties proposées ; ne pas croire qu’un délimiteur suffit.
- Refuser toute élévation de droit, révélation de secret ou changement de route demandé par une pièce.
- Les outils ont des schémas fermés, des opérations explicitement permises et des limites de volume.
- Revalider droits, préconditions et montants côté serveur même après confirmation utilisateur.
- Aucun SQL, code arbitraire, commande shell ou URL libre fourni par le modèle n’est exécutable.
- Les sorties réseau éventuelles sont limitées côté serveur ; bloquer accès internes et redirections non autorisées.
- Les imports imposent limites de taille, formats admis et traitements isolés sans exécution de contenu actif.
- Ne pas charger un fichier de production dans un outil externe de diagnostic non autorisé.
- Tester exfiltration, injection indirecte, confusion de tenant et contournement des confirmations.

## 6. Inférence, secrets et zéro rétention

- La clé OpenRouter disponible n’est ni lue pour ce travail ni copiée dans les documents.
- En exploitation, les secrets restent côté serveur, hors prompts, navigateur, dépôt et journaux.
- Prévoir séparation des environnements, droits minimaux, rotation, révocation et plafonds de dépenses.
- Inventorier pour chaque route le modèle, l’opérateur aval, les régions et tous les sous-traitants concernés.
- Vérifier conservation, entraînement, journaux d’abus, métadonnées, support et exceptions contractuelles.
- Conserver les engagements datés et les réglages techniques démontrant le zéro rétention exigé.
- Toute route de repli doit satisfaire les mêmes contrôles ; interdire le repli silencieux non conforme.
- Réévaluer le dossier après changement de modèle, de route, d’opérateur ou de conditions.
- Retirer identités et détails inutiles avant envoi ; préférer des calculs locaux sur les données originales.
- Une table de correspondance ou un contexte réidentifiant implique une pseudonymisation, pas un anonymat garanti.
- La table éventuelle reste locale au traitement autorisé, cloisonnée et exclue du prompt.
- En cas de preuve insuffisante, bloquer le flux sensible et proposer un parcours local ou une revue humaine.

## 7. Canaux et données professionnelles sensibles

- Le web chat S1 est proposé ; sécuriser transport, sessions, pièces jointes et affichage des contenus.
- Telegram reste souhaité, avec calendrier à arbitrer ; aucune décision de report n’est actée.
- Avant ouverture, qualifier bots, stockage, destinataires, transferts et limites de confidentialité du canal.
- Ne pas assimiler un échange avec un bot Telegram à une conversation chiffrée de bout en bout.
- Prévoir notifications minimales et renvoi vers un espace authentifié plutôt que pièces ou montants sensibles.
- L’e-mail connecté est après S1 ; son activation future exigera consentements ou bases appropriées et droits minimaux.
- Ses risques incluent usurpation, pièces malveillantes, transfert involontaire et injection via messages entrants.
- En santé, pour les avocats et les vétérinaires, seul le traitement de leur administration propre est visé.
- Les dossiers patients ou clients sont exclus ; une facture peut néanmoins révéler des informations sensibles ou secrètes.
- Qualifier au cas par cas données de santé, exigences HDS, secret professionnel, contrats et transferts.
- Ni l’exclusion des dossiers ni la localisation française ne dispensent de cette qualification ; bloquer les cas non validés.

## 8. Conservation, audit et restauration

- Définir une matrice par catégorie : finalité, accès, durée, obligation applicable, purge et justification.
- Distinguer pièces comptables, écritures validées, brouillons, conversations, secrets et traces techniques.
- Les obligations légales de conservation peuvent limiter l’effacement ; elles ne justifient pas de tout conserver.
- Prévoir traitement documenté des demandes RGPD, restriction d’accès et réponse motivée aux exceptions applicables.
- L’append-only concerne les écritures validées, pas toutes les données personnelles ni tous les journaux.
- L’audit conserve acteur, organisation, action, objet, date, règle et validation, sans secrets ni contenu intégral inutile.
- Protéger l’audit contre altération et accès excessifs ; une empreinte seule n’établit pas la conformité.
- Chiffrer transport, stockage et sauvegardes avec gestion des clés distincte des copies sauvegardées.
- Proposer des sauvegardes isolées, avec objectifs de perte maximale et de reprise à fixer avant bêta réelle.
- Tester la restauration sur environnement isolé, cohérence des écritures et récupération des pièces comprises.
- Documenter expiration des copies et réapplication des suppressions après restauration pour éviter la résurrection des données.

## 9. Responsabilité métier et gestion d’incident

- Le self-service et la responsabilité de l’utilisateur ne dispensent pas d’examiner les règles d’exercice réglementé.
- Délimiter les prestations comptables et juridiques, les actes réservés et les besoins de revue professionnelle.
- Un audit ou une attestation d’un partenaire comptable n’est pas une certification légale de commissaire aux comptes.
- Un résultat incertain expose limites, sources et besoin de revue ; il ne devient pas fiable par répétition du modèle.
- Les actions engageantes affichent effets, destinataire et données avant une confirmation adaptée au risque.
- Prévoir arrêt des traitements, révocation des clés, isolement des tenants affectés et conservation proportionnée des preuves.
- Qualifier rapidement l’incident, ses impacts et les obligations de notification selon les délais applicables.
- Désigner responsables et procédure de contact avant ouverture ; tester le scénario de fuite et celui de restauration.

## 10. Conditions bloquantes de release MVP avec données réelles

Ces conditions restent celles de l’ouverture MVP concernée ; la recette MTP fictive applique les conditions proportionnées de la section MTP, sans revendiquer les garanties ci-dessous.

- Preuves de cloisonnement et d’autorisation objet/action, y compris exports et traitements différés ; tests d’accès entre entreprises.
- Validation des routes d’inférence sensibles, secrets protégés et absence de repli non conforme.
- Tests réussis des calculs, arrondis, écritures, idempotence, confirmations et injections prioritaires.
- Règles applicables validées et mécanisme effectif de blocage des règles périmées ou douteuses.
- Revue des traitements, contrats, transferts, qualifications sectorielles et limites d’exercice réglementé.
- Restauration démontrée, politique de conservation exploitable et procédure d’incident attribuée.
- TESE ne peut être activé sans accès autorisé, mandat et éligibilité établis ; sinon fonctionnalité bloquée.
- Aucun jalon ni plafond budgétaire ne permet d’assouplir ces conditions ; bloquer l’ouverture concernée et soumettre tout changement de périmètre au porteur.

Les mécanismes proposés sont décrits dans [ARCHITECTURE.md](ARCHITECTURE.md).
Consigner les arbitrages dans [DECISIONS.md](DECISIONS.md) et les travaux et preuves dans [SUIVI.md](SUIVI.md).
