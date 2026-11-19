# ÉCHAP — Périmètre de référence

Statut : périmètre demandé et arbitrages actés, pas inventaire de fonctions déjà livrées. Date : 2026-11-10.

## 1. Règles de lecture

Séparer cinq axes : activité, forme juridique, régime fiscal, régime social et TVA. BNC et BIC désignent des catégories fiscales, pas des formes juridiques ; l’IS est un impôt. Une activité libérale en société à l’IS ne se traite pas comme une entreprise individuelle en BNC. Le régime micro n’implique pas automatiquement la franchise de TVA.

Pour le MVP, la couverture doit être décrite par profil et par opération, avec preuves et tests. « Dans la cible » signifie « à couvrir », pas « tous les cas sont déjà conformes ». Aucune restriction sectorielle, géographique interne à la France, de devise ou de volume n’a été approuvée pour simplifier silencieusement ses sprints.

## MTP — première version testable avant le MVP

Le **MTP (Minimum Testable Product)** précède le MVP. Il consiste à rendre l’existant Paperasse utilisable par un testeur depuis un navigateur, sans Claude Code, agent préalable, terminal, installation locale ni clé personnelle d’inférence.

### Surface du MTP

| Skill existant | Domaine expérimenté sur cas fictifs |
| --- | --- |
| `comptable` | Comptabilité, fiscalité d’entreprise, facturation et documents |
| `fiscaliste` | Fiscalité personnelle et simulations existantes |
| `notaire` | Immobilier, SCI, famille, successions et donations |
| `controleur-fiscal` | Simulation de contrôle fiscal |
| `commissaire-aux-comptes` | Analyse et simulation d’audit, pas certification légale |
| `syndic` | Copropriété et documents de gestion existants |

Les connecteurs existants font également partie de cette expérimentation (Qonto, Stripe, Pennylane, sources publiques) en **sandbox si disponible, sinon en simulation identifiée**, sur données fictives exclusivement.

### Enveloppe et limites

- Chat web hébergé, dépôt de pièces fictives, consultation et téléchargement des résultats.
- Espaces testeurs protégés et isolés ; pas de partage collaboratif ni de portail expert-comptable.
- Stack, agent et hébergement libres pour ce jalon : viser la rapidité de mise à disposition et le réemploi.
- Données fictives exclusivement : aucune donnée ni pièce réelle autorisée.
- Pas de TESE ni de nouveau moteur métier pour ce jalon.

## 2. Populations du sprint 1 du MVP

| ID | Population demandée | Précisions et conséquences |
| --- | --- | --- |
| CIB-01 | Tous les micro-entrepreneurs, quelle que soit l’activité éligible à ce régime | Commerce, artisanat, services et activités mixtes inclus ; pas seulement micro-BNC. Les métiers exclus légalement du régime ne deviennent pas éligibles par le produit. |
| CIB-02 | Activités BNC sans salariés ni stagiaires | Inclure gestion courante et déclarations, micro-BNC et déclaration contrôlée selon le profil ; ne pas limiter aux consultants non réglementés. |
| CIB-03 | Sociétés exerçant les autres activités libérales visées, sans équipe salariée hors associés/mandataires | Inclure structures unipersonnelles et pluripersonnelles ; traiter chaque forme et régime, pas un modèle BNC unique. |
| CIB-04 | Sociétés à l’IS sans équipe salariée hors associés/mandataires | Exemple explicitement demandé : SAS avec deux associés mandataires sociaux. Aucun plafond de CA propre au sprint n’a été acté. |
| CIB-05 | Médecins, vétérinaires et avocats en collaboration libérale | Pour ces trois professions, la collaboration libérale est la limite initiale demandée. Vérifier statut, exercice autorisé, fiscalité, cotisations et règles déontologiques ; ne pas supposer l’IS toujours applicable. |
| CIB-06 | SCI, en s’alignant sur Paperasse | Audit nécessaire des fonctions réellement documentées, codées et testées. Les références SCI IR/IS ne suffisent pas à établir une génération déclarative validée. |

Les populations se recoupent. Elles ne constituent pas six modules indépendants à dupliquer.

### Frontières à expliciter, sans exclusion implicite

- Micro-entrepreneurs employeurs : la demande « toutes activités » ne précise pas si l’absence de salariés s’applique aussi à cette population. Leur paie ne relève pas du sprint 1 hors exception mandataires ; faire arbitrer la couverture du dossier.
- Associés titulaires d’un contrat de travail distinct de leur mandat : obligations et éligibilité TESE à distinguer du mandat seul ; aucune dispense de paie n’est présumée.
- Stagiaires dans les sociétés à l’IS : absence explicitement demandée pour les BNC ; portée générale à confirmer.
- Stocks, caisse (exigence NF 525 pour commerces physiques/restauration exclue du S1), BTP (situations de chantier, TVA multi-taux), commerce international (DEB/OSS), devises, territoires ultramarins et régimes particuliers : cartographier les obligations déclenchées par la cible large. Un cas non validé doit être visible et bloqué, pas automatiquement traité comme un cas simple.
- Pour les SCI, nature des locations, TVA, associés personnes physiques/morales et opérations patrimoniales : frontière exacte à dériver de l’audit et à faire confirmer.

Les artistes-auteurs ont été évoqués comme extension ; leur régime propre n’a pas été confirmé dans le dernier périmètre du sprint 1. Ne pas le confondre avec le statut de micro-entrepreneur.

## Accès au MVP

Selon DEC-025, chaque entreprise dispose d’un seul utilisateur dans son espace sécurisé. Plusieurs testeurs peuvent utiliser ÉCHAP en parallèle, chacun dans l’espace isolé de son entreprise ; ce n’est pas une instance unique pour tous. Authentification, autorisation et isolation entre entreprises restent obligatoires.

Les invitations, rôles collaboratifs, accès partagés et accès direct d’un expert-comptable à un espace sont reportés après le MVP, sans date de livraison actée. Cela ne supprime pas la revue compétente requise des règles et sorties sensibles. Des associés ou mandataires peuvent figurer dans le dossier sans avoir de compte. La gestion éventuelle de plusieurs entreprises par un même utilisateur reste à préciser.

## 3. Domaines fonctionnels du sprint 1

Tous les domaines ci-dessous font partie du cadrage, pas seulement les lignes comptables.

| Domaine | Gestion courante et sorties attendues | Contrôle de couverture |
| --- | --- | --- |
| Administration | Profil de l’entreprise, associés/mandataires, démarches et dossier administratif | Applicabilité, pièces, échéances et état de chaque démarche |
| Documents | Dépôt local, classement, recherche, liens vers opérations, préparation de dossiers | Original préservé, provenance, accès, doublons, intégrité |
| Facturation | Devis, factures, honoraires, acomptes, avoirs, suivi des règlements | Mentions, numérotation, TVA et formats applicables validés |
| Comptabilité | Imports CSV/OFX, qualification, rapprochement, recettes/dépenses, immobilisations, clôture selon profil | Invariants, justificatifs, historique, règles fiscales et comptables applicables |
| Fiscalité et déclarations | Calculs, préparation des déclarations et annexes selon profil, contrôle et export | Liste des obligations par profil, millésime et sources ; aucun dépôt fiscal au sprint 1 |
| Réglementaire | Calendrier, alertes, pièces manquantes, conformité documentaire et facturation électronique | Ne pas présenter une obligation comme satisfaite sans preuve |
| Juridique de l’activité | Préparation encadrée de contrats, courriers, décisions sociales, approbations et checklists | Contexte validé, source, modèle versionné, limites des actes réservés |
| Recouvrement | Suivi des impayés, calculs applicables, projets de relances/mises en demeure et dossiers de recours | Créance, débiteur, preuve, délais et pénalités vérifiés ; pas d’envoi ni de dépôt automatique |
| Vérifications d’entreprises | Structuration des informations disponibles, contrôle de cohérence, dossier de risque | S1 à partir de pièces/données fournies ; ne pas prétendre à une recherche publique actualisée sans intégration |
| Dirigeants | Rémunération, frais, dividendes, obligations et préparation des décisions selon statut | TESE privilégié pour mandataires éligibles ; pas de moteur de paie maison |
| Assistance et conseil | Explication, choix encadrés et préparation d’actions dans les domaines précédents | Sources et hypothèses séparées, escalade humaine pour interprétation non sûre |

Au MVP, les successions, donations, régimes matrimoniaux, opérations patrimoniales privées et gestion de copropriétés présents dans Paperasse ne sont pas automatiquement intégrés au produit professionnel. Leur expérimentation fictive au MTP ne tranche pas leur inclusion ultérieure ; leur frontière avec l’administration d’une SCI reste à arbitrer.

## 4. Déclarations : préparer n’est pas déposer

Le sprint 1 doit couvrir la génération des déclarations applicables aux profils demandés. Une liste exhaustive, millésimée et validée reste à construire, y compris les obligations sociales hors salariés.

| Profil | Familles à inventorier et valider, sans prétendre à une liste exhaustive |
| --- | --- |
| Micro | Déclarations de CA, éléments de déclaration de revenus professionnels, TVA et autres obligations selon activité/options |
| BNC en déclaration contrôlée | 2035 et annexes applicables, TVA et obligations sociales/fiscales du professionnel |
| Sociétés à l’IS | 2065 et annexes du régime applicable, liasse simplifiée ou normale, TVA, rémunérations/distributions et autres obligations |
| SCI | Obligations IR/IS et associés selon situation ; frontière des générateurs à confirmer par audit de Paperasse |
| Mandataires éligibles TESE | Informations et processus requis par le service ; bulletins et formalités réalisés par TESE, avec états de traitement et preuves |

Un micro-entrepreneur n’a pas automatiquement une liasse ; l’IS n’impose pas toujours les tableaux du réel normal ; le FEC n’est pas une sortie universelle pour tous les profils. Les exports sont conditionnés aux obligations réelles.

## 5. Intégrations et canaux

### Sprint 1

- Imports locaux CSV/OFX et dépôt de documents ; compatibilité par format réellement testé, pas « tous fichiers de toutes banques ».
- TESE : exception explicite aux intégrations métier, uniquement pour les mandataires éligibles. Adhésion, autorisation d’accès et voie technique à démontrer. Le service peut accomplir des formalités sociales : cette exception n’autorise pas les autres transmissions.
- Inférence via OpenRouter : fournisseur envisagé pour le MVP, distinct des intégrations métier ; activation conditionnée aux exigences de confidentialité.
- Chat web et visualisation : premier canal proposé. Web + Telegram est la direction produit actée ; le calendrier Telegram doit être arbitré, pas reporté silencieusement.

### Hors sprint 1, à traiter immédiatement après

Agrégation bancaire, Stripe, email connecté et collecte/OCR intégrée, signature électronique dont Documenso, transmission des déclarations fiscales/liasses, appels aux sources publiques d’entreprises. Aucun fournisseur choisi automatiquement, aucune interface `BankProvider` à préparer avant le besoin.

L’extraction d’un document déposé localement fait partie du parcours à spécifier ; elle ne vaut pas décision sur un fournisseur OCR ni intégration d’une messagerie.

## 6. Sprint 2 et extensions

- Étendre aux salariés via TESE, sous réserve d’éligibilité et de vérification des situations exclues ; cela ne couvre pas automatiquement tous les besoins RH.
- Intégrer les services externes prioritaires, après comparaison des coûts, accès, licences et garanties.
- Approfondir les cas artisans, TPE de services jusqu’à 2 M€ de CA et 10 salariés, artistes-auteurs et e-commerce à volume modéré. Ces axes historiques ne réduisent pas la cible micro/IS déjà demandée au sprint 1.
- Étudier l’option d’intervention d’un expert-comptable partenaire ; la disponibilité effective d’un partenaire n’est pas établie.

## 7. Porte de validation du MVP et de l’usage réel

Pour chaque couple profil/opération : règles applicables identifiées, sources et millésime validés, outil contrôlé, tests probants, statut de sécurité acceptable et limites affichées. Une déclaration produite à titre expérimental reste un brouillon non exploitable.

Une dépendance bloquée reste une partie du périmètre demandé avec statut bloqué. Toute réduction de cible ou déplacement de fonction nécessite un arbitrage explicite dans [DECISIONS.md](DECISIONS.md).
