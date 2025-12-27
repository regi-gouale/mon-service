# Feature Specification: Church Team Management SaaS

**Feature Branch**: `001-church-team-management`
**Created**: 2025-12-27
**Status**: Draft
**Input**: SaaS de gestion d'équipes pour les départements d'église permettant d'organiser les plannings, la communication et la logistique des services et événements.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Inscription et Authentification (Priority: P1)

Un utilisateur peut créer un compte, se connecter de manière sécurisée et accéder à l'application selon son rôle (administrateur, membre ou invité). L'authentification supporte l'email/mot de passe et OAuth Google.

**Why this priority**: Sans authentification, aucune autre fonctionnalité n'est utilisable. C'est le fondement de toute l'application et la première interaction de chaque utilisateur.

**Independent Test**: Peut être testé en créant un compte, en se connectant, et en vérifiant que l'accès aux fonctionnalités correspond au rôle attribué.

**Acceptance Scenarios**:

1. **Given** un visiteur sur la page d'accueil, **When** il clique sur "S'inscrire" et remplit le formulaire avec un email valide et un mot de passe conforme, **Then** un compte est créé et un email de confirmation est envoyé
2. **Given** un utilisateur avec un compte existant, **When** il se connecte avec ses identifiants corrects, **Then** il accède au tableau de bord correspondant à son rôle
3. **Given** un utilisateur sur la page de connexion, **When** il clique sur "Se connecter avec Google", **Then** il est redirigé vers Google OAuth et connecté après autorisation
4. **Given** un utilisateur ayant oublié son mot de passe, **When** il demande une réinitialisation, **Then** il reçoit un email avec un lien sécurisé valide 24 heures

---

### User Story 2 - Saisie des Indisponibilités (Priority: P1)

Un membre d'équipe peut renseigner ses jours d'indisponibilité pour un mois donné. Le responsable reçoit une notification lorsqu'un membre met à jour ses disponibilités.

**Why this priority**: La saisie des indisponibilités est le prérequis indispensable à la génération des plannings. Sans cette fonctionnalité, le planning ne peut pas être créé de manière équitable.

**Independent Test**: Un membre peut ouvrir le calendrier du mois, sélectionner des jours, valider, et voir ses indisponibilités enregistrées.

**Acceptance Scenarios**:

1. **Given** un membre connecté, **When** il accède à la page "Mes indisponibilités" et sélectionne plusieurs jours du mois à venir, **Then** ces jours sont enregistrés et affichés en surbrillance
2. **Given** un membre ayant des indisponibilités enregistrées, **When** il modifie ses sélections, **Then** les modifications sont sauvegardées et le responsable est notifié
3. **Given** la date limite de saisie passée, **When** un membre tente de modifier ses indisponibilités, **Then** le système affiche un message indiquant que la période de saisie est terminée

---

### User Story 3 - Génération et Publication du Planning (Priority: P1)

Un responsable peut générer automatiquement le planning mensuel en tenant compte des indisponibilités, des compétences requises et de l'équité de rotation entre les membres. Il peut ajuster manuellement puis publier le planning.

**Why this priority**: Le planning est la fonctionnalité centrale de l'application. Il représente la valeur principale pour les utilisateurs et justifie l'adoption du produit.

**Independent Test**: Le responsable lance la génération, visualise le planning proposé, fait des ajustements, publie, et les membres reçoivent leurs affectations.

**Acceptance Scenarios**:

1. **Given** tous les membres ont saisi leurs indisponibilités, **When** le responsable clique sur "Générer le planning", **Then** un planning est créé en respectant les contraintes d'indisponibilité
2. **Given** un planning généré, **When** le responsable déplace manuellement un membre d'un créneau à un autre, **Then** le système vérifie la compatibilité et applique la modification
3. **Given** un planning finalisé, **When** le responsable clique sur "Publier", **Then** tous les membres reçoivent une notification avec leurs affectations
4. **Given** un planning publié, **When** un membre consulte son tableau de bord, **Then** il voit uniquement ses propres affectations mises en évidence

---

### User Story 4 - Gestion des Membres du Département (Priority: P2)

Un responsable peut ajouter, modifier ou retirer des membres de son département. Il peut également attribuer des rôles et définir les compétences de chaque membre.

**Why this priority**: La gestion des membres est nécessaire pour constituer l'équipe avant de pouvoir créer des plannings. Elle dépend de l'authentification mais précède logiquement la gestion des plannings.

**Independent Test**: Le responsable peut inviter un nouveau membre par email, celui-ci crée son compte et apparaît dans la liste des membres du département.

**Acceptance Scenarios**:

1. **Given** un responsable sur la page "Équipe", **When** il invite un nouveau membre par email, **Then** une invitation est envoyée et apparaît en statut "En attente"
2. **Given** une invitation en attente, **When** l'invité clique sur le lien et crée son compte, **Then** il rejoint automatiquement le département avec le rôle "Membre"
3. **Given** un responsable visualisant la liste des membres, **When** il modifie les compétences d'un membre, **Then** ces compétences sont prises en compte dans les futures générations de planning
4. **Given** un responsable, **When** il retire un membre du département, **Then** ce membre perd l'accès aux fonctionnalités du département mais conserve son compte

---

### User Story 5 - Notifications et Rappels (Priority: P2)

Les utilisateurs reçoivent des notifications pour les événements importants : nouvelles affectations, rappels avant un service, demandes d'indisponibilités, annonces du responsable.

**Why this priority**: Les notifications garantissent que les membres sont informés à temps de leurs obligations, réduisant les absences non planifiées.

**Independent Test**: Un membre reçoit une notification 24h avant un service auquel il est affecté et peut la consulter dans l'application.

**Acceptance Scenarios**:

1. **Given** un planning publié, **When** un membre est affecté à un service, **Then** il reçoit une notification immédiate avec les détails du service
2. **Given** un service prévu dans 24 heures, **When** l'heure de rappel arrive, **Then** le membre affecté reçoit un rappel avec l'heure et le dress code
3. **Given** un responsable, **When** il envoie une annonce à l'équipe, **Then** tous les membres reçoivent une notification dans l'application
4. **Given** un utilisateur, **When** il configure ses préférences de notification, **Then** il peut activer/désactiver les emails tout en gardant les notifications in-app

---

### User Story 6 - Gestion du Code Vestimentaire (Priority: P3)

Un responsable peut définir le dress code pour chaque type de service ou événement, avec des images de référence. Les membres consultent le dress code applicable à leurs affectations.

**Why this priority**: Le dress code améliore la cohésion visuelle de l'équipe mais n'est pas bloquant pour l'utilisation principale de l'application.

**Independent Test**: Le responsable crée un dress code avec image, l'associe à un service, et le membre peut le visualiser depuis son affectation.

**Acceptance Scenarios**:

1. **Given** un responsable sur la page "Dress codes", **When** il crée un nouveau dress code avec nom, description et photo, **Then** celui-ci est sauvegardé et disponible
2. **Given** un dress code existant, **When** le responsable l'associe à un type de service, **Then** tous les services de ce type affichent automatiquement ce dress code
3. **Given** un membre consultant son affectation, **When** un dress code est défini, **Then** il voit la description et l'image de référence

---

### User Story 7 - Comptes-Rendus de Service (Priority: P3)

Après un service, un membre peut créer un compte-rendu incluant les présences, les points forts, les améliorations suggérées et des photos. Les autres membres du département peuvent consulter ces rapports.

**Why this priority**: Les comptes-rendus permettent l'amélioration continue mais ne sont pas essentiels au fonctionnement quotidien.

**Independent Test**: Un membre crée un rapport après un service, l'enregistre, et les autres membres peuvent le consulter dans l'historique.

**Acceptance Scenarios**:

1. **Given** un membre après un service, **When** il crée un nouveau rapport et remplit les champs requis, **Then** le rapport est enregistré et visible par l'équipe
2. **Given** un rapport en cours de création, **When** le membre ajoute des photos, **Then** les images sont attachées au rapport
3. **Given** un membre consultant l'historique, **When** il recherche par date ou type de service, **Then** les rapports correspondants sont affichés

---

### User Story 8 - Gestion de l'Inventaire (Priority: P3)

Les membres peuvent consulter et mettre à jour l'inventaire du matériel du département. Ils peuvent signaler un équipement endommagé ou manquant.

**Why this priority**: L'inventaire facilite la logistique mais peut être géré manuellement dans un premier temps.

**Independent Test**: Un membre ajoute un nouvel équipement à l'inventaire, modifie son état, et ces informations sont visibles par tous.

**Acceptance Scenarios**:

1. **Given** un membre sur la page "Inventaire", **When** il ajoute un nouvel article avec nom, catégorie et état, **Then** l'article apparaît dans la liste
2. **Given** un article existant, **When** un membre change son état en "À réparer", **Then** une alerte est créée pour le responsable
3. **Given** un membre, **When** il attribue temporairement un équipement à lui-même, **Then** l'attribution est enregistrée avec une date de retour prévue

---

### User Story 9 - Calendrier des Dates Importantes (Priority: P4)

Les membres peuvent consulter et contribuer au calendrier partagé contenant les anniversaires, voyages et événements importants du département.

**Why this priority**: Fonctionnalité "nice-to-have" qui renforce la cohésion d'équipe mais n'est pas essentielle aux opérations.

**Independent Test**: Un membre ajoute son anniversaire, et les autres membres peuvent le voir dans le calendrier du mois.

**Acceptance Scenarios**:

1. **Given** un membre sur la page "Calendrier", **When** il ajoute un voyage prévu, **Then** la date apparaît dans le calendrier partagé
2. **Given** un anniversaire dans les 7 prochains jours, **When** un membre consulte le tableau de bord, **Then** l'anniversaire à venir est affiché

---

### User Story 10 - Liste de Courses Partagée (Priority: P4)

Les membres peuvent créer et gérer collaborativement des listes d'achats pour le département, marquer les articles achetés et voir l'historique.

**Why this priority**: Fonctionnalité complémentaire qui facilite la logistique mais peut être gérée par d'autres moyens.

**Independent Test**: Un membre crée une liste, ajoute des articles, un autre membre marque un article comme acheté.

**Acceptance Scenarios**:

1. **Given** un membre sur la page "Courses", **When** il crée une nouvelle liste et ajoute des articles, **Then** la liste est visible par toute l'équipe
2. **Given** une liste existante, **When** un membre marque un article comme acheté, **Then** l'article est barré et le nom de l'acheteur est affiché

---

### Edge Cases

- Que se passe-t-il si un membre n'a saisi aucune indisponibilité avant la date limite ? → Le système considère qu'il est disponible tous les jours et l'inclut dans la rotation normale
- Comment gérer un conflit où aucun membre n'est disponible pour un créneau ? → Le système signale le conflit au responsable qui doit résoudre manuellement
- Que faire si un membre quitte le département après publication du planning ? → Le responsable reçoit une alerte et doit réaffecter manuellement les services concernés
- Comment gérer un membre sans compétences définies ? → Il ne sera pas affecté aux services nécessitant des compétences spécifiques
- Que se passe-t-il si l'email d'invitation n'est jamais ouvert ? → L'invitation expire après 7 jours et le responsable peut renvoyer une nouvelle invitation

## Requirements _(mandatory)_

### Functional Requirements

#### Authentification & Utilisateurs

- **FR-001**: Le système DOIT permettre l'inscription par email avec validation
- **FR-002**: Le système DOIT supporter l'authentification OAuth2 via Google
- **FR-003**: Le système DOIT gérer trois rôles : Administrateur, Membre, Invité
- **FR-004**: Le système DOIT permettre la récupération de mot de passe par email
- **FR-005**: Le système DOIT permettre à chaque utilisateur de gérer son profil (nom, contact, photo)

#### Gestion des Départements

- **FR-006**: Le système DOIT permettre la création de départements avec nom et description
- **FR-007**: Le système DOIT isoler complètement les données entre départements différents
- **FR-008**: Le système DOIT permettre l'invitation de membres par email
- **FR-009**: Le système DOIT permettre la définition de compétences/rôles par membre

#### Gestion des Plannings

- **FR-010**: Le système DOIT permettre la saisie des indisponibilités par mois
- **FR-011**: Le système DOIT générer automatiquement un planning en respectant les contraintes
- **FR-012**: Le système DOIT permettre l'ajustement manuel du planning après génération
- **FR-013**: Le système DOIT notifier les membres lors de la publication du planning
- **FR-014**: Le système DOIT permettre l'export du planning en PDF et iCal
- **FR-015**: Le système DOIT assurer une rotation équitable basée sur l'historique des participations

#### Code Vestimentaire

- **FR-016**: Le système DOIT permettre la création de dress codes avec images
- **FR-017**: Le système DOIT associer les dress codes aux types de services

#### Comptes-Rendus

- **FR-018**: Le système DOIT permettre la création de rapports post-service
- **FR-019**: Le système DOIT permettre l'attachement de photos aux rapports
- **FR-020**: Le système DOIT archiver et rendre recherchables les rapports passés

#### Inventaire

- **FR-021**: Le système DOIT permettre le catalogage du matériel
- **FR-022**: Le système DOIT permettre le suivi de l'état du matériel
- **FR-023**: Le système DOIT générer des alertes pour matériel endommagé ou manquant

#### Notifications

- **FR-024**: Le système DOIT envoyer des notifications in-app pour tous les événements importants
- **FR-025**: Le système DOIT envoyer des rappels configurables avant les services
- **FR-026**: Le système DOIT permettre la configuration des préférences de notification par utilisateur

### Key Entities

- **Utilisateur**: Personne utilisant l'application. Attributs : nom, email, rôle, photo, préférences de notification
- **Département**: Groupe/équipe au sein d'une église. Attributs : nom, description, paramètres de planification
- **Membre**: Relation entre un utilisateur et un département. Attributs : compétences, date d'adhésion, statut
- **Service**: Événement ou culte nécessitant des membres. Attributs : date, heure, type, lieu, dress code associé
- **Planning**: Ensemble des affectations pour une période. Attributs : mois, statut (brouillon/publié), date de publication
- **Affectation**: Attribution d'un membre à un service. Attributs : membre, service, rôle assigné
- **Indisponibilité**: Période où un membre n'est pas disponible. Attributs : dates, raison (optionnelle)
- **DressCode**: Tenue vestimentaire définie. Attributs : nom, description, images de référence
- **Rapport**: Compte-rendu post-service. Attributs : date, auteur, contenu, photos, service concerné
- **Article**: Élément d'inventaire. Attributs : nom, catégorie, état, attributaire actuel
- **Notification**: Message système. Attributs : type, contenu, destinataire, statut lu/non-lu

## Assumptions

- Chaque utilisateur ne peut être membre que d'un seul département à la fois dans la version initiale
- Les services se répètent généralement sur une base hebdomadaire (dimanche matin, mercredi soir, etc.)
- La date limite de saisie des indisponibilités est fixée par le responsable (par défaut : 7 jours avant la génération du planning)
- Un membre peut avoir plusieurs compétences (musicien, technicien son, accueil, etc.)
- L'application cible principalement les smartphones, mais doit rester utilisable sur desktop
- Les notifications email sont optionnelles, les notifications in-app sont toujours actives
- La rétention des données suit les standards RGPD (données supprimées 3 ans après inactivité)

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 80% des membres utilisent l'application pour saisir leurs indisponibilités dans les 3 premiers mois
- **SC-002**: Le temps de création d'un planning mensuel est réduit de 70% par rapport au processus manuel
- **SC-003**: Les pages de l'application se chargent en moins de 2 secondes pour 95% des utilisateurs
- **SC-004**: La génération automatique du planning prend moins de 10 secondes
- **SC-005**: Aucun conflit de planning (membre affecté alors qu'indisponible) ne passe la validation
- **SC-006**: Score de satisfaction utilisateur supérieur à 4/5 dans les enquêtes mensuelles
- **SC-007**: 90% des utilisateurs complètent la saisie de leurs indisponibilités sans assistance
- **SC-008**: Taux de notification lue supérieur à 70% dans les 24 heures
- **SC-009**: L'application atteint un score d'accessibilité WCAG 2.1 niveau AA
- **SC-010**: Zéro incident de sécurité lié aux données personnelles dans la première année
