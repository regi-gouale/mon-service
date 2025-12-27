# Data Model: Church Team Management SaaS

**Feature**: 001-church-team-management
**Date**: 2025-12-27
**Purpose**: Définir les entités, relations et règles de validation

## Diagramme des Relations

```
┌─────────────────┐       ┌─────────────────┐
│  Organization   │───1:N─│   Department    │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │1:N                      │1:N
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│      User       │───1:1─│     Member      │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │                    ┌────┴────┐
         │                    │         │
         │                    │1:N      │1:N
         │                    ▼         ▼
         │           ┌────────────┐  ┌────────────────┐
         │           │Availability│  │PlanningAssign. │
         │           └────────────┘  └───────┬────────┘
         │                                   │N:1
         │                                   ▼
         │                          ┌─────────────────┐
         │                          │    Planning     │
         │                          └────────┬────────┘
         │                                   │N:1
         │                                   ▼
         │                          ┌─────────────────┐
         └──────────────────────────│    Service      │
                                    └─────────────────┘
                                             │N:1
                                             ▼
                                    ┌─────────────────┐
                                    │   DressCode     │
                                    └─────────────────┘
```

## Entités

### 1. Organization

Représente une église ou une organisation utilisant le SaaS.

| Champ        | Type         | Contraintes             | Description              |
| ------------ | ------------ | ----------------------- | ------------------------ |
| `id`         | UUID         | PK, auto-generated      | Identifiant unique       |
| `name`       | VARCHAR(255) | NOT NULL                | Nom de l'organisation    |
| `slug`       | VARCHAR(100) | UNIQUE, NOT NULL        | Identifiant URL-friendly |
| `logo_url`   | VARCHAR(500) | NULLABLE                | URL du logo              |
| `settings`   | JSONB        | DEFAULT '{}'            | Paramètres personnalisés |
| `created_at` | TIMESTAMP    | NOT NULL, DEFAULT NOW() | Date de création         |
| `updated_at` | TIMESTAMP    | NOT NULL                | Dernière modification    |

**Index** : `slug` (UNIQUE)

**Règles de validation** :

- `name` : 2-255 caractères
- `slug` : 2-100 caractères, lowercase, alphanumeric + hyphens

---

### 2. User

Représente un utilisateur de l'application.

| Champ                      | Type         | Contraintes                 | Description                                 |
| -------------------------- | ------------ | --------------------------- | ------------------------------------------- |
| `id`                       | UUID         | PK, auto-generated          | Identifiant unique                          |
| `organization_id`          | UUID         | FK → Organization, NULLABLE | Organisation actuelle                       |
| `email`                    | VARCHAR(255) | UNIQUE, NOT NULL            | Email (identifiant)                         |
| `password_hash`            | VARCHAR(255) | NULLABLE                    | Hash du mot de passe (null si OAuth)        |
| `first_name`               | VARCHAR(100) | NOT NULL                    | Prénom                                      |
| `last_name`                | VARCHAR(100) | NOT NULL                    | Nom de famille                              |
| `phone`                    | VARCHAR(20)  | NULLABLE                    | Numéro de téléphone                         |
| `avatar_url`               | VARCHAR(500) | NULLABLE                    | URL de la photo de profil                   |
| `role`                     | ENUM         | NOT NULL, DEFAULT 'member'  | Rôle global (admin, manager, member, guest) |
| `email_verified`           | BOOLEAN      | DEFAULT FALSE               | Email vérifié                               |
| `is_active`                | BOOLEAN      | DEFAULT TRUE                | Compte actif                                |
| `notification_preferences` | JSONB        | DEFAULT '{}'                | Préférences de notification                 |
| `last_login_at`            | TIMESTAMP    | NULLABLE                    | Dernière connexion                          |
| `created_at`               | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création                            |
| `updated_at`               | TIMESTAMP    | NOT NULL                    | Dernière modification                       |

**Index** :

- `email` (UNIQUE)
- `organization_id`

**Enum `UserRole`** : `admin`, `manager`, `member`, `guest`

**Règles de validation** :

- `email` : format email valide
- `password` : min 8 caractères, 1 majuscule, 1 chiffre, 1 spécial (si non OAuth)
- `phone` : format international E.164

---

### 3. Department

Représente un département/équipe au sein d'une organisation.

| Champ                        | Type         | Contraintes                 | Description                 |
| ---------------------------- | ------------ | --------------------------- | --------------------------- |
| `id`                         | UUID         | PK, auto-generated          | Identifiant unique          |
| `organization_id`            | UUID         | FK → Organization, NOT NULL | Organisation parente        |
| `name`                       | VARCHAR(255) | NOT NULL                    | Nom du département          |
| `description`                | TEXT         | NULLABLE                    | Description                 |
| `settings`                   | JSONB        | DEFAULT '{}'                | Paramètres de planification |
| `availability_deadline_days` | INTEGER      | DEFAULT 7                   | Jours avant deadline saisie |
| `is_active`                  | BOOLEAN      | DEFAULT TRUE                | Département actif           |
| `created_at`                 | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création            |
| `updated_at`                 | TIMESTAMP    | NOT NULL                    | Dernière modification       |
| `created_by`                 | UUID         | FK → User, NOT NULL         | Créateur                    |

**Index** :

- `organization_id`
- `(organization_id, name)` (UNIQUE)

**Règles de validation** :

- `name` : 2-255 caractères, unique par organisation
- `availability_deadline_days` : 1-30

---

### 4. Member

Représente l'appartenance d'un utilisateur à un département.

| Champ             | Type      | Contraintes                 | Description              |
| ----------------- | --------- | --------------------------- | ------------------------ |
| `id`              | UUID      | PK, auto-generated          | Identifiant unique       |
| `organization_id` | UUID      | FK → Organization, NOT NULL | Clé de tenant            |
| `department_id`   | UUID      | FK → Department, NOT NULL   | Département              |
| `user_id`         | UUID      | FK → User, NOT NULL         | Utilisateur              |
| `role`            | ENUM      | NOT NULL, DEFAULT 'member'  | Rôle dans le département |
| `skills`          | VARCHAR[] | DEFAULT '{}'                | Compétences (array)      |
| `status`          | ENUM      | NOT NULL, DEFAULT 'active'  | Statut                   |
| `joined_at`       | TIMESTAMP | NOT NULL, DEFAULT NOW()     | Date d'adhésion          |
| `created_at`      | TIMESTAMP | NOT NULL, DEFAULT NOW()     | Date de création         |
| `updated_at`      | TIMESTAMP | NOT NULL                    | Dernière modification    |

**Index** :

- `organization_id`
- `department_id`
- `user_id`
- `(department_id, user_id)` (UNIQUE)

**Enum `MemberRole`** : `admin`, `manager`, `member`

**Enum `MemberStatus`** : `pending`, `active`, `inactive`

**Règles de validation** :

- Un utilisateur ne peut être membre d'un département qu'une seule fois
- `skills` : array de strings, max 20 compétences

---

### 5. Invitation

Représente une invitation à rejoindre un département.

| Champ             | Type         | Contraintes                 | Description        |
| ----------------- | ------------ | --------------------------- | ------------------ |
| `id`              | UUID         | PK, auto-generated          | Identifiant unique |
| `organization_id` | UUID         | FK → Organization, NOT NULL | Clé de tenant      |
| `department_id`   | UUID         | FK → Department, NOT NULL   | Département cible  |
| `email`           | VARCHAR(255) | NOT NULL                    | Email de l'invité  |
| `role`            | ENUM         | NOT NULL, DEFAULT 'member'  | Rôle proposé       |
| `token`           | VARCHAR(100) | UNIQUE, NOT NULL            | Token d'invitation |
| `status`          | ENUM         | NOT NULL, DEFAULT 'pending' | Statut             |
| `expires_at`      | TIMESTAMP    | NOT NULL                    | Date d'expiration  |
| `accepted_at`     | TIMESTAMP    | NULLABLE                    | Date d'acceptation |
| `invited_by`      | UUID         | FK → User, NOT NULL         | Invitant           |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création   |

**Index** :

- `organization_id`
- `token` (UNIQUE)
- `email`

**Enum `InvitationStatus`** : `pending`, `accepted`, `expired`, `cancelled`

**Règles de validation** :

- `token` : généré automatiquement (64 caractères aléatoires)
- `expires_at` : 7 jours après création par défaut

---

### 6. Service

Représente un service/culte/événement nécessitant des membres.

| Champ             | Type         | Contraintes                 | Description                         |
| ----------------- | ------------ | --------------------------- | ----------------------------------- |
| `id`              | UUID         | PK, auto-generated          | Identifiant unique                  |
| `organization_id` | UUID         | FK → Organization, NOT NULL | Clé de tenant                       |
| `department_id`   | UUID         | FK → Department, NOT NULL   | Département                         |
| `name`            | VARCHAR(255) | NOT NULL                    | Nom du service                      |
| `service_type`    | VARCHAR(100) | NOT NULL                    | Type (culte, répétition, événement) |
| `date`            | DATE         | NOT NULL                    | Date du service                     |
| `start_time`      | TIME         | NOT NULL                    | Heure de début                      |
| `end_time`        | TIME         | NULLABLE                    | Heure de fin                        |
| `location`        | VARCHAR(255) | NULLABLE                    | Lieu                                |
| `dress_code_id`   | UUID         | FK → DressCode, NULLABLE    | Code vestimentaire                  |
| `required_roles`  | JSONB        | DEFAULT '[]'                | Rôles requis avec quantités         |
| `notes`           | TEXT         | NULLABLE                    | Notes                               |
| `is_recurring`    | BOOLEAN      | DEFAULT FALSE               | Service récurrent                   |
| `recurrence_rule` | VARCHAR(255) | NULLABLE                    | Règle RRULE (iCal)                  |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création                    |
| `updated_at`      | TIMESTAMP    | NOT NULL                    | Dernière modification               |
| `created_by`      | UUID         | FK → User, NOT NULL         | Créateur                            |

**Index** :

- `organization_id`
- `department_id`
- `date`
- `(department_id, date)`

**Format `required_roles`** :

```json
[
  { "role": "musicien", "count": 3 },
  { "role": "technicien_son", "count": 1 },
  { "role": "accueil", "count": 2 }
]
```

**Règles de validation** :

- `date` : doit être dans le futur pour création
- `start_time` < `end_time` si end_time défini

---

### 7. Planning

Représente un planning mensuel pour un département.

| Champ              | Type      | Contraintes                 | Description              |
| ------------------ | --------- | --------------------------- | ------------------------ |
| `id`               | UUID      | PK, auto-generated          | Identifiant unique       |
| `organization_id`  | UUID      | FK → Organization, NOT NULL | Clé de tenant            |
| `department_id`    | UUID      | FK → Department, NOT NULL   | Département              |
| `month`            | DATE      | NOT NULL                    | Premier jour du mois     |
| `status`           | ENUM      | NOT NULL, DEFAULT 'draft'   | Statut du planning       |
| `confidence_score` | FLOAT     | NULLABLE                    | Score de confiance (0-1) |
| `generated_at`     | TIMESTAMP | NULLABLE                    | Date de génération       |
| `published_at`     | TIMESTAMP | NULLABLE                    | Date de publication      |
| `created_at`       | TIMESTAMP | NOT NULL, DEFAULT NOW()     | Date de création         |
| `updated_at`       | TIMESTAMP | NOT NULL                    | Dernière modification    |
| `created_by`       | UUID      | FK → User, NOT NULL         | Créateur                 |

**Index** :

- `organization_id`
- `(department_id, month)` (UNIQUE)

**Enum `PlanningStatus`** : `draft`, `generated`, `published`, `archived`

**Règles de validation** :

- `month` : toujours le premier jour du mois
- Un seul planning par département par mois

---

### 8. PlanningAssignment

Représente l'affectation d'un membre à un service dans un planning.

| Champ             | Type         | Contraintes                  | Description           |
| ----------------- | ------------ | ---------------------------- | --------------------- |
| `id`              | UUID         | PK, auto-generated           | Identifiant unique    |
| `organization_id` | UUID         | FK → Organization, NOT NULL  | Clé de tenant         |
| `planning_id`     | UUID         | FK → Planning, NOT NULL      | Planning parent       |
| `service_id`      | UUID         | FK → Service, NOT NULL       | Service concerné      |
| `member_id`       | UUID         | FK → Member, NOT NULL        | Membre affecté        |
| `assigned_role`   | VARCHAR(100) | NOT NULL                     | Rôle assigné          |
| `status`          | ENUM         | NOT NULL, DEFAULT 'assigned' | Statut                |
| `confirmed_at`    | TIMESTAMP    | NULLABLE                     | Date de confirmation  |
| `notes`           | TEXT         | NULLABLE                     | Notes                 |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()      | Date de création      |
| `updated_at`      | TIMESTAMP    | NOT NULL                     | Dernière modification |

**Index** :

- `organization_id`
- `planning_id`
- `service_id`
- `member_id`
- `(service_id, member_id)` (UNIQUE)

**Enum `AssignmentStatus`** : `assigned`, `confirmed`, `declined`, `replaced`

**Règles de validation** :

- Un membre ne peut être affecté qu'une fois par service

---

### 9. Availability

Représente les indisponibilités d'un membre.

| Champ             | Type         | Contraintes                 | Description              |
| ----------------- | ------------ | --------------------------- | ------------------------ |
| `id`              | UUID         | PK, auto-generated          | Identifiant unique       |
| `organization_id` | UUID         | FK → Organization, NOT NULL | Clé de tenant            |
| `member_id`       | UUID         | FK → Member, NOT NULL       | Membre                   |
| `date`            | DATE         | NOT NULL                    | Date d'indisponibilité   |
| `reason`          | VARCHAR(255) | NULLABLE                    | Raison (optionnel)       |
| `is_all_day`      | BOOLEAN      | DEFAULT TRUE                | Journée entière          |
| `start_time`      | TIME         | NULLABLE                    | Heure début (si partiel) |
| `end_time`        | TIME         | NULLABLE                    | Heure fin (si partiel)   |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création         |
| `updated_at`      | TIMESTAMP    | NOT NULL                    | Dernière modification    |

**Index** :

- `organization_id`
- `member_id`
- `(member_id, date)` (UNIQUE)

**Règles de validation** :

- Une seule entrée par membre par date
- Si `is_all_day = false`, `start_time` et `end_time` requis

---

### 10. DressCode

Représente un code vestimentaire.

| Champ             | Type         | Contraintes                 | Description           |
| ----------------- | ------------ | --------------------------- | --------------------- |
| `id`              | UUID         | PK, auto-generated          | Identifiant unique    |
| `organization_id` | UUID         | FK → Organization, NOT NULL | Clé de tenant         |
| `department_id`   | UUID         | FK → Department, NOT NULL   | Département           |
| `name`            | VARCHAR(255) | NOT NULL                    | Nom                   |
| `description`     | TEXT         | NULLABLE                    | Description           |
| `image_urls`      | VARCHAR[]    | DEFAULT '{}'                | URLs des images       |
| `is_active`       | BOOLEAN      | DEFAULT TRUE                | Actif                 |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création      |
| `updated_at`      | TIMESTAMP    | NOT NULL                    | Dernière modification |
| `created_by`      | UUID         | FK → User, NOT NULL         | Créateur              |

**Index** :

- `organization_id`
- `department_id`

**Règles de validation** :

- `image_urls` : max 5 images par dress code

---

### 11. InventoryItem

Représente un article d'inventaire.

| Champ             | Type         | Contraintes                 | Description           |
| ----------------- | ------------ | --------------------------- | --------------------- |
| `id`              | UUID         | PK, auto-generated          | Identifiant unique    |
| `organization_id` | UUID         | FK → Organization, NOT NULL | Clé de tenant         |
| `department_id`   | UUID         | FK → Department, NOT NULL   | Département           |
| `name`            | VARCHAR(255) | NOT NULL                    | Nom de l'article      |
| `category`        | VARCHAR(100) | NOT NULL                    | Catégorie             |
| `description`     | TEXT         | NULLABLE                    | Description           |
| `quantity`        | INTEGER      | DEFAULT 1                   | Quantité              |
| `condition`       | ENUM         | NOT NULL, DEFAULT 'good'    | État                  |
| `image_url`       | VARCHAR(500) | NULLABLE                    | Photo                 |
| `assigned_to`     | UUID         | FK → Member, NULLABLE       | Membre attributaire   |
| `assigned_until`  | DATE         | NULLABLE                    | Date de retour prévue |
| `notes`           | TEXT         | NULLABLE                    | Notes                 |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création      |
| `updated_at`      | TIMESTAMP    | NOT NULL                    | Dernière modification |
| `created_by`      | UUID         | FK → User, NOT NULL         | Créateur              |

**Index** :

- `organization_id`
- `department_id`
- `category`

**Enum `ItemCondition`** : `new`, `good`, `fair`, `needs_repair`, `damaged`, `disposed`

---

### 12. ServiceReport

Représente un compte-rendu de service.

| Champ             | Type      | Contraintes                 | Description           |
| ----------------- | --------- | --------------------------- | --------------------- |
| `id`              | UUID      | PK, auto-generated          | Identifiant unique    |
| `organization_id` | UUID      | FK → Organization, NOT NULL | Clé de tenant         |
| `department_id`   | UUID      | FK → Department, NOT NULL   | Département           |
| `service_id`      | UUID      | FK → Service, NOT NULL      | Service concerné      |
| `author_id`       | UUID      | FK → Member, NOT NULL       | Auteur                |
| `content`         | TEXT      | NOT NULL                    | Contenu du rapport    |
| `highlights`      | TEXT      | NULLABLE                    | Points forts          |
| `improvements`    | TEXT      | NULLABLE                    | Points à améliorer    |
| `attendees`       | UUID[]    | DEFAULT '{}'                | Membres présents      |
| `absentees`       | UUID[]    | DEFAULT '{}'                | Membres absents       |
| `image_urls`      | VARCHAR[] | DEFAULT '{}'                | Photos attachées      |
| `created_at`      | TIMESTAMP | NOT NULL, DEFAULT NOW()     | Date de création      |
| `updated_at`      | TIMESTAMP | NOT NULL                    | Dernière modification |

**Index** :

- `organization_id`
- `department_id`
- `service_id`

---

### 13. Event

Représente un événement du calendrier (anniversaire, voyage, etc.).

| Champ             | Type         | Contraintes                 | Description                    |
| ----------------- | ------------ | --------------------------- | ------------------------------ |
| `id`              | UUID         | PK, auto-generated          | Identifiant unique             |
| `organization_id` | UUID         | FK → Organization, NOT NULL | Clé de tenant                  |
| `department_id`   | UUID         | FK → Department, NULLABLE   | Département (null si org-wide) |
| `member_id`       | UUID         | FK → Member, NULLABLE       | Membre concerné                |
| `event_type`      | ENUM         | NOT NULL                    | Type d'événement               |
| `title`           | VARCHAR(255) | NOT NULL                    | Titre                          |
| `description`     | TEXT         | NULLABLE                    | Description                    |
| `date`            | DATE         | NOT NULL                    | Date                           |
| `end_date`        | DATE         | NULLABLE                    | Date de fin (si période)       |
| `is_recurring`    | BOOLEAN      | DEFAULT FALSE               | Récurrent annuellement         |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création               |
| `updated_at`      | TIMESTAMP    | NOT NULL                    | Dernière modification          |
| `created_by`      | UUID         | FK → User, NOT NULL         | Créateur                       |

**Index** :

- `organization_id`
- `department_id`
- `date`

**Enum `EventType`** : `birthday`, `trip`, `holiday`, `meeting`, `other`

---

### 14. ShoppingList

Représente une liste de courses.

| Champ             | Type         | Contraintes                 | Description           |
| ----------------- | ------------ | --------------------------- | --------------------- |
| `id`              | UUID         | PK, auto-generated          | Identifiant unique    |
| `organization_id` | UUID         | FK → Organization, NOT NULL | Clé de tenant         |
| `department_id`   | UUID         | FK → Department, NOT NULL   | Département           |
| `name`            | VARCHAR(255) | NOT NULL                    | Nom de la liste       |
| `status`          | ENUM         | NOT NULL, DEFAULT 'active'  | Statut                |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création      |
| `updated_at`      | TIMESTAMP    | NOT NULL                    | Dernière modification |
| `created_by`      | UUID         | FK → User, NOT NULL         | Créateur              |

**Index** :

- `organization_id`
- `department_id`

**Enum `ListStatus`** : `active`, `completed`, `archived`

---

### 15. ShoppingItem

Représente un article dans une liste de courses.

| Champ              | Type         | Contraintes                 | Description           |
| ------------------ | ------------ | --------------------------- | --------------------- |
| `id`               | UUID         | PK, auto-generated          | Identifiant unique    |
| `organization_id`  | UUID         | FK → Organization, NOT NULL | Clé de tenant         |
| `shopping_list_id` | UUID         | FK → ShoppingList, NOT NULL | Liste parente         |
| `name`             | VARCHAR(255) | NOT NULL                    | Nom de l'article      |
| `category`         | VARCHAR(100) | NULLABLE                    | Catégorie             |
| `quantity`         | INTEGER      | DEFAULT 1                   | Quantité              |
| `unit`             | VARCHAR(50)  | NULLABLE                    | Unité                 |
| `is_purchased`     | BOOLEAN      | DEFAULT FALSE               | Acheté                |
| `purchased_by`     | UUID         | FK → Member, NULLABLE       | Acheteur              |
| `purchased_at`     | TIMESTAMP    | NULLABLE                    | Date d'achat          |
| `assigned_to`      | UUID         | FK → Member, NULLABLE       | Responsable assigné   |
| `created_at`       | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création      |
| `updated_at`       | TIMESTAMP    | NOT NULL                    | Dernière modification |

**Index** :

- `organization_id`
- `shopping_list_id`

---

### 16. Notification

Représente une notification utilisateur.

| Champ             | Type         | Contraintes                 | Description            |
| ----------------- | ------------ | --------------------------- | ---------------------- |
| `id`              | UUID         | PK, auto-generated          | Identifiant unique     |
| `organization_id` | UUID         | FK → Organization, NOT NULL | Clé de tenant          |
| `user_id`         | UUID         | FK → User, NOT NULL         | Destinataire           |
| `type`            | VARCHAR(100) | NOT NULL                    | Type de notification   |
| `title`           | VARCHAR(255) | NOT NULL                    | Titre                  |
| `message`         | TEXT         | NOT NULL                    | Message                |
| `data`            | JSONB        | DEFAULT '{}'                | Données additionnelles |
| `is_read`         | BOOLEAN      | DEFAULT FALSE               | Lu                     |
| `read_at`         | TIMESTAMP    | NULLABLE                    | Date de lecture        |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT NOW()     | Date de création       |

**Index** :

- `organization_id`
- `user_id`
- `(user_id, is_read)`
- `created_at`

**Types de notification** : `planning_published`, `assignment_reminder`, `availability_reminder`, `birthday_reminder`, `report_created`, `announcement`

---

### 17. RefreshToken

Représente un refresh token pour l'authentification.

| Champ         | Type         | Contraintes             | Description        |
| ------------- | ------------ | ----------------------- | ------------------ |
| `id`          | UUID         | PK, auto-generated      | Identifiant unique |
| `user_id`     | UUID         | FK → User, NOT NULL     | Utilisateur        |
| `token_hash`  | VARCHAR(255) | NOT NULL                | Hash du token      |
| `device_info` | VARCHAR(255) | NULLABLE                | Info appareil      |
| `expires_at`  | TIMESTAMP    | NOT NULL                | Expiration         |
| `is_revoked`  | BOOLEAN      | DEFAULT FALSE           | Révoqué            |
| `created_at`  | TIMESTAMP    | NOT NULL, DEFAULT NOW() | Date de création   |

**Index** :

- `user_id`
- `token_hash`

---

## Migrations Alembic

### Migration Initiale

```
migrations/versions/
├── 001_initial_schema.py       # Tables de base (org, user, department, member)
├── 002_planning_tables.py      # Service, planning, assignment, availability
├── 003_features_tables.py      # DressCode, inventory, reports
├── 004_collaboration_tables.py # Events, shopping lists
├── 005_notifications.py        # Notifications
└── 006_add_indexes.py          # Index de performance
```

---

## Champs d'Audit Communs

Toutes les tables incluent ces champs de base via un mixin :

```python
class AuditMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
```
