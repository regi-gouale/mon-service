# GitHub Issues - Church Team Management SaaS

Ce fichier contient toutes les issues à créer sur GitHub depuis le fichier `tasks.md`.

**Branch**: `001-church-team-management`  
**Feature**: Church Team Management SaaS  
**Total Issues**: 135 tâches

---

## Comment utiliser ce fichier

1. Chaque bloc représente une issue GitHub
2. Copier/coller le contenu dans "New Issue" sur GitHub
3. Assigner aux développeurs responsables
4. Lier au projet `Church Team Management`

---

## Epic 0: Infrastructure & Fondations

### Issue T0.1.1 - Initialiser le repository avec structure backend/ et frontend/

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 2h

**Description**:
Initialiser la structure du monorepo avec les dossiers `backend/` et `frontend/` suivant la Clean Architecture.

**Acceptance Criteria**:
- [ ] Dossiers `backend/` et `frontend/` créés
- [ ] Structure de base dans chaque dossier
- [ ] README.md à la racine avec instructions de setup
- [ ] Fichiers `.gitignore` appropriés

**Related to**: Plan: [plan.md](../specs/001-church-team-management/plan.md)

---

### Issue T0.1.2 - Créer docker-compose.yml avec PostgreSQL, Redis, MailHog, MinIO

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1.5h

**Description**:
Créer le fichier `docker-compose.yml` à la racine du projet avec tous les services nécessaires pour le développement local.

**Services requis**:
- PostgreSQL 15+ (port 5432)
- Redis 7+ (port 6379)
- MailHog (ports 1025 SMTP, 8025 web)
- MinIO (ports 9000 API, 9001 console) - *optionnel*

**Acceptance Criteria**:
- [ ] Tous les services démarrent sans erreur: `docker compose up -d`
- [ ] Healthchecks implémentés
- [ ] Volumes persistants configurés
- [ ] Logging configuré

**Related to**: [quickstart.md](../specs/001-church-team-management/quickstart.md)

---

### Issue T0.1.3 - Configurer les fichiers .env.example pour backend et frontend

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1h

**Description**:
Créer les fichiers `.env.example` dans `backend/` et `frontend/` avec toutes les variables d'environnement nécessaires.

**Variables Backend**:
- APP_NAME, APP_ENV, DEBUG
- DATABASE_URL, REDIS_URL
- JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
- S3_ENDPOINT_URL, S3_ACCESS_KEY_ID, etc.
- SMTP_HOST, SMTP_PORT, MAIL_FROM

**Variables Frontend**:
- NEXT_PUBLIC_API_URL
- NEXT_PUBLIC_WS_URL
- BETTER_AUTH_SECRET, BETTER_AUTH_URL
- NEXT_PUBLIC_ENABLE_ANALYTICS

**Acceptance Criteria**:
- [ ] `.env.example` dans backend/ avec toutes les variables
- [ ] `.env.example` dans frontend/ avec toutes les variables
- [ ] Commentaires explicatifs pour chaque variable
- [ ] Aucune valeur secrète réelle

**Related to**: [quickstart.md](../specs/001-church-team-management/quickstart.md)

---

### Issue T0.1.4 - Créer le Makefile racine avec commandes unifiées

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 1h

**Description**:
Créer un `Makefile` à la racine avec les commandes principales pour le développement.

**Commandes requises**:
```bash
make up              # Docker compose up
make down            # Docker compose down
make install         # Install dependencies (backend + frontend)
make dev             # Lancer dev servers
make test            # Lancer tous les tests
make lint            # Lancer tous les linters
make format          # Formatter le code
make migrate         # Appliquer les migrations
```

**Acceptance Criteria**:
- [ ] Makefile créé à la racine
- [ ] Toutes les commandes fonctionnent
- [ ] Help message avec `make help`
- [ ] Dokumenté dans README

---

### Issue T0.1.5 - Configurer pre-commit hooks (ruff, eslint, prettier, commitlint)

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 1.5h

**Description**:
Configurer les pre-commit hooks pour vérifier la qualité du code avant chaque commit.

**Hooks à configurer**:
- ruff (Python linting)
- prettier (frontend formatting)
- commitlint (conventional commits)
- no-commit-to-branch (protection main/master)

**Acceptance Criteria**:
- [ ] `.pre-commit-config.yaml` créé
- [ ] Hooks s'exécutent avant commit
- [ ] Commits non-conformes sont bloqués
- [ ] Documentation pour ignorer hooks si nécessaire

---

### Issue T0.2.1 - Initialiser projet Python avec pyproject.toml et uv

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1h

**Description**:
Initialiser le projet Python dans `backend/` avec `pyproject.toml` et gérer les dépendances avec `uv`.

**Contenu pyproject.toml**:
- Métadonnées du projet (name, version, description)
- Python version requirement (3.11+)
- Dépendances principales
- Dépendances de développement
- Scripts pytest, mypy, ruff

**Acceptance Criteria**:
- [ ] `pyproject.toml` créé avec toutes les sections
- [ ] `uv venv` crée l'environnement virtuel
- [ ] Dépendances installées avec `uv pip install -r requirements.txt`
- [ ] `.venv/` dans `.gitignore`

---

### Issue T0.2.2 - Créer structure Clean Architecture

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 2h

**Description**:
Créer la structure de répertoires suivant Clean Architecture dans `backend/app/`.

**Structure requise**:
```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── domain/
│   │   ├── entities/
│   │   └── value_objects/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── worker.py
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml
└── Makefile
```

**Acceptance Criteria**:
- [ ] Tous les répertoires créés
- [ ] `__init__.py` dans chaque dossier
- [ ] Structure prête pour le code

---

### Issue T0.2.3 - Configurer app/core/config.py avec Pydantic Settings

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1.5h

**Description**:
Créer la classe Settings avec Pydantic v2 pour gérer les variables d'environnement.

**Configuration à inclure**:
- APP_NAME, APP_ENV, DEBUG
- DATABASE settings (url, pool_size, echo)
- REDIS settings
- JWT settings (secret_key, algorithm, expiry times)
- CORS_ORIGINS
- S3 settings
- SMTP settings
- Celery settings

**Acceptance Criteria**:
- [ ] `Settings` class créée avec Pydantic v2
- [ ] Validation des variables d'environnement au startup
- [ ] Settings utilisable partout via `from app.core.config import settings`
- [ ] .env vars prennent priorité sur les defaults

---

### Issue T0.2.4 - Configurer SQLAlchemy 2.0 async avec app/core/database.py

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 2h

**Description**:
Configurer SQLAlchemy 2.0 avec support async pour la base de données PostgreSQL.

**Contenu app/core/database.py**:
- `AsyncEngine` et `async_sessionmaker`
- `get_db()` dependency pour FastAPI
- Connexion pooling
- Logging SQL (optionnel en dev)
- Context manager pour transactions

**Acceptance Criteria**:
- [ ] Engine créé avec URL async (postgresql+asyncpg)
- [ ] Sessions async fonctionnelles
- [ ] get_db() works avec FastAPI dependencies
- [ ] Connection pooling configuré

---

### Issue T0.2.5 - Configurer Alembic pour les migrations

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1.5h

**Description**:
Initialiser Alembic pour gérer les migrations de schéma de base de données.

**Configuration**:
- `alembic init` avec target_metadata
- Script `env.py` configuré pour async
- Première migration de base

**Acceptance Criteria**:
- [ ] `alembic/` directory créé
- [ ] `alembic.ini` configuré
- [ ] `alembic upgrade head` fonctionne
- [ ] Migrations avec `alembic revision --autogenerate`

---

### Issue T0.2.6 - Créer le fichier app/main.py avec CORS et middleware

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 2h

**Description**:
Créer le fichier principal FastAPI avec configuration de base.

**Contenu app/main.py**:
- FastAPI app instance
- CORS middleware
- Logging middleware
- Exception handlers
- Health check endpoint GET `/health`
- Include v1 routes (vides pour l'instant)
- Startup/shutdown events

**Acceptance Criteria**:
- [ ] App démarre sans erreur: `uvicorn app.main:app --reload`
- [ ] GET `/health` retourne 200
- [ ] CORS configuré selon .env
- [ ] Logs structurés

---

### Issue T0.2.7 - Configurer logging JSON structuré avec correlation_id

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 1.5h

**Description**:
Configurer la journalisation JSON structurée avec correlation_id pour tracer les requêtes.

**Requirements**:
- Tous les logs en JSON
- correlation_id généré par requête
- correlation_id dans les headers de réponse
- Support pour Loki/ELK stack

**Acceptance Criteria**:
- [ ] Logs sortent en JSON
- [ ] Chaque requête a correlation_id unique
- [ ] correlation_id visible dans logs et headers
- [ ] Documentation de configuration

---

### Issue T0.3.1 - Initialiser projet Next.js 14+ avec App Router et TypeScript strict

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1.5h

**Description**:
Initialiser le projet frontend Next.js 14+ avec App Router et TypeScript strict mode.

**Configuration**:
- `create-next-app@latest` avec options:
  - App Router: Yes
  - TypeScript: Yes
  - ESLint: Yes
  - Tailwind: Yes
  - Src directory: Yes
  - Turbopack: Yes (optionnel)

**Acceptance Criteria**:
- [ ] `next dev` démarre sans erreur
- [ ] `tsconfig.json` avec `"strict": true`
- [ ] `next lint` fonctionne
- [ ] Page d'accueil accessible sur http://localhost:3000

---

### Issue T0.3.2 - Configurer TailwindCSS et Shadcn/ui

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1h

**Description**:
Configurer TailwindCSS et installer les composants Shadcn/ui.

**Composants Shadcn à installer**:
- Button
- Input
- Card
- Dialog/Modal
- Dropdown Menu
- Select
- Table
- Badge
- Avatar
- Toast/Toaster

**Acceptance Criteria**:
- [ ] Tailwind fonctionne
- [ ] Shadcn/ui installé et configuré
- [ ] Composants importables depuis `@/components/ui`
- [ ] Dark mode support configurable

---

### Issue T0.3.3 - Créer structure dossiers frontend

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1.5h

**Description**:
Créer la structure de répertoires du frontend.

**Structure requise**:
```
frontend/src/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── register/
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── layout.tsx
├── components/
│   ├── ui/
│   ├── forms/
│   └── layouts/
├── lib/
│   ├── api.ts
│   ├── utils.ts
│   └── constants.ts
├── stores/
│   ├── auth.ts
│   └── ui.ts
├── hooks/
│   ├── useAuth.ts
│   └── useApi.ts
├── types/
│   └── index.ts
├── config/
│   └── site.ts
└── styles/
    └── globals.css
```

**Acceptance Criteria**:
- [ ] Structure créée
- [ ] Tous les layout.tsx en place
- [ ] Page racine dans app/

---

### Issue T0.3.4 - Configurer TanStack Query provider

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1h

**Description**:
Installer et configurer TanStack Query (React Query v5) pour la gestion du state serveur.

**Configuration**:
- Installer `@tanstack/react-query`
- Créer `QueryClientProvider` wrapper
- Configurer cache time, stale time, retry policies
- Créer hooks personnalisés pour API calls

**Acceptance Criteria**:
- [ ] `QueryClientProvider` dans root layout
- [ ] API requests utilisant useQuery/useMutation
- [ ] Caching et refetching fonctionnels
- [ ] Erreurs gérées proprement

---

### Issue T0.3.5 - Configurer Zustand store de base

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1h

**Description**:
Configurer Zustand pour la gestion du state client (authentification, UI).

**Stores initiaux**:
- `stores/auth.ts` - user, accessToken, isAuthenticated
- `stores/ui.ts` - theme, sidebarOpen, notifications

**Acceptance Criteria**:
- [ ] Zustand configuré
- [ ] Auth store fonctionnel
- [ ] Hooks de store utilisables partout
- [ ] Persistence (localStorage) pour auth

---

### Issue T0.3.6 - Créer client API avec fetch wrapper et gestion erreurs

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 2h

**Description**:
Créer un client API wrapper pour les appels HTTP avec gestion d'erreurs et interceptors.

**Features**:
- Wrapper autour de fetch
- Headers par défaut (Authorization, Content-Type)
- Retry logic avec exponential backoff
- Gestion des erreurs (401 -> refresh token, 403 -> redirect)
- Types génériques pour requêtes/réponses
- Support SSR (Server Components)

**Acceptance Criteria**:
- [ ] `lib/api.ts` créé
- [ ] API calls utilisent le wrapper
- [ ] Token refresh automatique
- [ ] Erreurs affichées proprement

---

### Issue T0.3.7 - Configurer next-intl pour i18n (fr par défaut)

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 1h

**Description**:
Configurer next-intl pour la gestion des traductions multilingues (français par défaut).

**Configuration**:
- Installer `next-intl`
- Créer messages.json pour FR et EN
- Configurer middleware next-intl
- Setup locale directory structure

**Acceptance Criteria**:
- [ ] i18n configuré
- [ ] Messages en FR disponibles
- [ ] Switchable à EN
- [ ] Locale persiste dans URL

---

### Issue T0.4.1 - Créer modèle Organization avec SQLAlchemy

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1.5h

**Description**:
Créer le modèle SQLAlchemy pour Organization (tenant principal).

**Champs**:
- id (UUID, PK)
- name (str, required)
- slug (str, unique)
- description (str, nullable)
- logo_url (str, nullable)
- is_active (bool, default True)
- created_at (datetime, auto)
- updated_at (datetime, auto)

**Relations**:
- users (OneToMany)
- departments (OneToMany)

**Acceptance Criteria**:
- [ ] Modèle créé dans `app/models/organization.py`
- [ ] Constraints et validations en place
- [ ] Indexes créés (slug unique)
- [ ] Testable avec pytest

---

### Issue T0.4.2 - Créer modèle User avec SQLAlchemy

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 2h

**Description**:
Créer le modèle User avec champs d'authentification et profil.

**Champs**:
- id (UUID, PK)
- email (str, unique, required)
- first_name (str, required)
- last_name (str, required)
- password_hash (str, required)
- phone (str, nullable)
- avatar_url (str, nullable)
- is_active (bool, default True)
- email_verified (bool, default False)
- created_at (datetime, auto)
- updated_at (datetime, auto)
- organization_id (UUID, FK, required)

**Relations**:
- organization (ManyToOne)
- refresh_tokens (OneToMany)
- members (OneToMany)
- notifications (OneToMany)

**Acceptance Criteria**:
- [ ] Modèle complet dans `app/models/user.py`
- [ ] Index sur email et organization_id
- [ ] Password hasher intégré (bcrypt)
- [ ] Soft delete support (nullable deleted_at)

---

### Issue T0.4.3 - Créer modèle RefreshToken

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1h

**Description**:
Créer le modèle pour gérer les refresh tokens.

**Champs**:
- id (UUID, PK)
- user_id (UUID, FK, required)
- token (str, unique, required)
- expires_at (datetime, required)
- created_at (datetime, auto)
- is_revoked (bool, default False)

**Relations**:
- user (ManyToOne)

**Acceptance Criteria**:
- [ ] Modèle créé
- [ ] Index sur (user_id, expires_at)
- [ ] Cleanup tokens expirés possible

---

### Issue T0.4.4 - Générer migration initiale Alembic

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1h

**Description**:
Générer la première migration Alembic avec les modèles Organization, User, RefreshToken.

**Steps**:
1. Ajouter modèles à `Base.metadata`
2. Configurer `env.py` avec target_metadata
3. `alembic revision --autogenerate -m "Initial schema"`
4. Vérifier le fichier généré

**Acceptance Criteria**:
- [ ] Migration file créé dans `alembic/versions/`
- [ ] Contient CREATE TABLE pour 3 modèles
- [ ] Contient les indexes et constraints
- [ ] `alembic upgrade head` fonctionne

---

### Issue T0.4.5 - Créer script de seed pour données de test

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 1.5h

**Description**:
Créer un script pour peupler la DB avec données de test.

**Données de test**:
- 1 Organization (Test Church)
- 5 Users (admin + 4 members)
- 2 Departments (Praise & Worship, Ushers)
- Services for next month

**Script**: `backend/app/scripts/seed_dev.py`

**Acceptance Criteria**:
- [ ] Script créé et exécutable
- [ ] `python -m app.scripts.seed_dev` peuple DB
- [ ] Données cohérentes et testables
- [ ] Script idempotent (peut s'exécuter plusieurs fois)

---

### Issue T0.4.6 - Tester la connexion DB et migrations

**Epic**: Infrastructure  
**Priority**: 🔴 Critical  
**Effort**: 1h

**Description**:
Vérifier que la connexion DB et les migrations fonctionnent correctement.

**Tests**:
- [ ] Docker compose PostgreSQL démarre
- [ ] `alembic upgrade head` fonctionne
- [ ] Tables sont créées dans la DB
- [ ] Seed script remplit les données
- [ ] Requêtes SELECT fonctionnent

**Acceptance Criteria**:
- [ ] DB fully operational
- [ ] Pas d'erreurs de connexion
- [ ] Documentation dans `docs/database.md`

---

### Issue T0.5.1 - Créer workflow GitHub Actions pour tests backend

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 2h

**Description**:
Créer un workflow GitHub Actions qui exécute les tests backend sur chaque push/PR.

**Workflow**:
- Déclenché: push sur main et PR
- Services: PostgreSQL, Redis
- Steps:
  1. Checkout code
  2. Setup Python 3.11
  3. Install dependencies
  4. Run pytest
  5. Upload coverage

**Acceptance Criteria**:
- [ ] Workflow créé dans `.github/workflows/test-backend.yml`
- [ ] Tests passent sur chaque PR
- [ ] Coverage reports générés
- [ ] Badges README mis à jour

---

### Issue T0.5.2 - Créer workflow GitHub Actions pour tests frontend

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 2h

**Description**:
Créer un workflow GitHub Actions pour tester le frontend.

**Workflow**:
- Déclenché: push sur main et PR
- Node version: 20+
- Steps:
  1. Checkout
  2. Setup Node
  3. Install dependencies
  4. Run linter
  5. Run type check
  6. Run tests (Vitest)
  7. Build check

**Acceptance Criteria**:
- [ ] Workflow créé dans `.github/workflows/test-frontend.yml`
- [ ] Build succeeds on every PR
- [ ] Linting passes
- [ ] Type checking passes

---

### Issue T0.5.3 - Configurer coverage reports (Codecov ou similaire)

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 1.5h

**Description**:
Configurer Codecov (ou similaire) pour tracker la couverture de tests.

**Configuration**:
- Backend coverage.xml depuis pytest
- Frontend coverage.json depuis Vitest
- Upload à Codecov
- Badges dans README
- PR comments avec coverage delta

**Acceptance Criteria**:
- [ ] Coverage rapports générés
- [ ] Codecov intégré
- [ ] Badges dans README
- [ ] PR comments affichent delta

---

### Issue T0.5.4 - Créer workflow de lint sur chaque PR

**Epic**: Infrastructure  
**Priority**: 🟡 Important  
**Effort**: 1.5h

**Description**:
Créer un workflow GitHub Actions pour vérifier la qualité du code.

**Linters**:
- Backend: ruff, mypy
- Frontend: eslint, prettier
- Commits: commitlint

**Acceptance Criteria**:
- [ ] Workflow créé dans `.github/workflows/lint.yml`
- [ ] Tous les linters s'exécutent
- [ ] Lint errors bloquent la merge

---

### Issue T0.5.5 - Documenter le workflow de déploiement

**Epic**: Infrastructure  
**Priority**: 🟢 Nice-to-have  
**Effort**: 1.5h

**Description**:
Créer documentation pour le processus de déploiement.

**Documentation**:
- Backend: Dokploy deployment
- Frontend: Vercel deployment
- Environment variables par environment
- Database migrations in production
- Rollback procedures

**Deliverable**: `docs/deployment.md`

**Acceptance Criteria**:
- [ ] Documentation écrite
- [ ] Deployment checklist
- [ ] Rollback procedures

---

## Epic 1: Inscription et Authentification (P1)

*(Voir tasks.md pour les 135+ issues complètes)*

---

## Résumé

Total des issues: **135+** tâches réparties sur **11 épics** + infrastructure

Pour importer dans GitHub:
1. Créer un projet "Church Team Management"
2. Importer les issues une par une (ou utiliser GitHub CLI)
3. Assigner par équipe (backend/frontend)
4. Lier les issues au projet
5. Configurer les milestones par phase
