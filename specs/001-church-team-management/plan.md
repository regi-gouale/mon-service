# Implementation Plan: Church Team Management SaaS

**Branch**: `001-church-team-management` | **Date**: 2025-12-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-church-team-management/spec.md`

## Summary

SaaS de gestion d'équipes pour les départements d'église permettant d'organiser les plannings, la communication et la logistique des services et événements. L'application comprend un frontend Next.js 14+ avec App Router et un backend FastAPI Python, utilisant PostgreSQL comme base de données principale avec Redis pour le cache et les tâches asynchrones.

**Fonctionnalités principales** :

- Authentification sécurisée (email/password + OAuth Google)
- Gestion des indisponibilités par les membres
- Génération automatique de plannings avec algorithme d'équité
- Notifications temps réel (WebSockets) et par email
- Gestion des codes vestimentaires, inventaire, rapports de service
- Multi-tenancy avec isolation par organisation

## Technical Context

**Language/Version**:

- Backend: Python 3.11+ avec type hints stricts
- Frontend: TypeScript strict (Next.js 14+)

**Primary Dependencies**:

- Backend: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Celery, python-socketio
- Frontend: Next.js 14 (App Router), TailwindCSS, Shadcn/ui, TanStack Query, Zustand, Better Auth

**Storage**:

- PostgreSQL 15+ (base principale, multi-tenancy par `organization_id`)
- Redis 7+ (cache, sessions, broker Celery)
- S3 compatible (Hetzner Object Storage) pour fichiers

**Testing**:

- Backend: pytest avec pytest-asyncio, coverage ≥ 80%
- Frontend: Vitest, Testing Library, coverage ≥ 70%

**Target Platform**:

- Backend: Linux server (Docker/Dokploy)
- Frontend: Vercel (Edge Runtime)
- Client: Navigateurs modernes, mobile-first responsive

**Project Type**: Web application (frontend + backend séparés)

**Performance Goals**:

- API: p95 < 200ms pour 95% des requêtes
- Frontend: LCP < 2.5s, FID < 100ms, CLS < 0.1
- Génération planning: < 10 secondes

**Constraints**:

- RGPD compliance (données personnelles)
- Multi-tenancy avec isolation stricte
- Mode hors-ligne basique (lecture planning)

**Scale/Scope**:

- 10+ organisations
- 100+ membres par organisation
- ~50 services/mois par département

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Principe I - Typage Strict & Stack Technique ✅

| Exigence                  | Conformité  | Notes                                                     |
| ------------------------- | ----------- | --------------------------------------------------------- |
| TypeScript `strict: true` | ✅ CONFORME | Configuré dans tsconfig.json                              |
| Next.js App Router + RSC  | ✅ CONFORME | Architecture App Router avec Server Components par défaut |
| TailwindCSS + Shadcn UI   | ✅ CONFORME | Stack UI spécifiée                                        |
| Better Auth               | ✅ CONFORME | Provider OAuth intégré                                    |
| Python 3.11+ type hints   | ✅ CONFORME | Python 3.11+ avec type hints stricts                      |
| Pydantic validation       | ✅ CONFORME | Pydantic v2 pour tous les schémas                         |
| Async/await               | ✅ CONFORME | SQLAlchemy 2.0 async, FastAPI async                       |
| PostgreSQL + SQLAlchemy   | ✅ CONFORME | PostgreSQL 15+ avec SQLAlchemy 2.0                        |
| Alembic migrations        | ✅ CONFORME | Alembic pour versioning schéma                            |

### Principe II - Architecture & Séparation des Couches ✅

| Exigence                      | Conformité  | Notes                                               |
| ----------------------------- | ----------- | --------------------------------------------------- |
| Routes sans logique métier    | ✅ CONFORME | Routes délèguent aux services                       |
| Services sans accès DB direct | ✅ CONFORME | Services utilisent repositories                     |
| Repositories pour DB          | ✅ CONFORME | Pattern repository implémenté                       |
| API versionnée `/api/v1/`     | ✅ CONFORME | Tous les endpoints sous `/api/v1/`                  |
| Endpoints kebab-case          | ✅ CONFORME | Ex: `/api/v1/dress-codes`, `/api/v1/shopping-lists` |

### Principe III - Qualité & Tests ✅

| Exigence                      | Conformité  | Notes                            |
| ----------------------------- | ----------- | -------------------------------- |
| Backend coverage ≥ 80%        | ✅ PLANIFIÉ | pytest avec coverage obligatoire |
| Frontend coverage ≥ 70%       | ✅ PLANIFIÉ | Vitest avec coverage obligatoire |
| Tests d'intégration critiques | ✅ PLANIFIÉ | Auth, planning, notifications    |
| Pre-commit hooks              | ✅ PLANIFIÉ | Ruff, ESLint, Prettier           |

### Principe IV - Sécurité ✅

| Exigence                    | Conformité  | Notes                                    |
| --------------------------- | ----------- | ---------------------------------------- |
| JWT + refresh tokens        | ✅ CONFORME | python-jose, 15min/7days expiration      |
| OAuth2 Google               | ✅ CONFORME | Better Auth frontend, validation backend |
| Validation client + serveur | ✅ CONFORME | Zod (frontend), Pydantic (backend)       |
| CSRF protection             | ✅ CONFORME | Implémenté via Better Auth               |
| Rate limiting               | ✅ CONFORME | Redis-based, 10 req/min sur auth         |
| Secrets via env vars        | ✅ CONFORME | Jamais en dur, .env.example fourni       |

### Principe V - Performance ✅

| Exigence        | Conformité  | Notes                               |
| --------------- | ----------- | ----------------------------------- |
| API p95 < 200ms | ✅ PLANIFIÉ | Monitoring Prometheus/Grafana       |
| Core Web Vitals | ✅ PLANIFIÉ | Next.js optimisations, lazy loading |
| Redis cache     | ✅ CONFORME | Cache plannings, sessions           |

### Principe VI - Expérience Développeur ✅

| Exigence             | Conformité  | Notes                       |
| -------------------- | ----------- | --------------------------- |
| README complet       | ✅ PLANIFIÉ | Setup < 5 minutes           |
| Docker Compose       | ✅ CONFORME | Environnement local complet |
| Hot reload           | ✅ CONFORME | Frontend et backend         |
| Logs JSON structurés | ✅ CONFORME | Correlation ID par requête  |

### Principe VII - Conventions & Standards ✅

| Exigence                       | Conformité  | Notes                         |
| ------------------------------ | ----------- | ----------------------------- |
| Commits conventionnels         | ✅ PLANIFIÉ | Pre-commit hook commitlint    |
| Branches feature/bugfix/hotfix | ✅ CONFORME | Workflow documenté            |
| Env vars SCREAMING_SNAKE_CASE  | ✅ CONFORME | DATABASE_URL, REDIS_URL, etc. |

**GATE RESULT**: ✅ PASS - Aucune violation de la constitution

## Project Structure

### Documentation (this feature)

```text
specs/001-church-team-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
│   ├── openapi.yaml
│   └── websocket-events.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
# Backend (FastAPI / Python)
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── __init__.py
│   │       │   ├── auth.py
│   │       │   ├── users.py
│   │       │   ├── organizations.py
│   │       │   ├── departments.py
│   │       │   ├── members.py
│   │       │   ├── plannings.py
│   │       │   ├── availabilities.py
│   │       │   ├── dress_codes.py
│   │       │   ├── inventory.py
│   │       │   ├── reports.py
│   │       │   ├── events.py
│   │       │   └── shopping_lists.py
│   │       └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── domain/
│   │   ├── entities/
│   │   └── value_objects/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── planning_generator.py
│   │   ├── notification_service.py
│   │   ├── email_service.py
│   │   └── file_storage_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── organization_repository.py
│   │   ├── department_repository.py
│   │   ├── member_repository.py
│   │   ├── planning_repository.py
│   │   ├── availability_repository.py
│   │   └── notification_repository.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── department.py
│   │   ├── member.py
│   │   ├── planning.py
│   │   ├── availability.py
│   │   ├── dress_code.py
│   │   ├── inventory_item.py
│   │   ├── service_report.py
│   │   ├── event.py
│   │   ├── shopping_list.py
│   │   └── notification.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── requests/
│   │   └── responses/
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── generate_planning.py
│   │       ├── send_notifications.py
│   │       └── send_emails.py
│   ├── websockets/
│   │   ├── __init__.py
│   │   └── handlers.py
│   └── main.py
├── migrations/
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── services/
│   │   └── repositories/
│   ├── integration/
│   │   └── api/
│   └── contract/
├── alembic.ini
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml

# Frontend (Next.js / TypeScript)
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── register/
│   │   │   │   └── page.tsx
│   │   │   ├── forgot-password/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── planning/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── [month]/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── generate/
│   │   │   │       └── page.tsx
│   │   │   ├── availabilities/
│   │   │   │   └── page.tsx
│   │   │   ├── dress-codes/
│   │   │   │   └── page.tsx
│   │   │   ├── inventory/
│   │   │   │   └── page.tsx
│   │   │   ├── reports/
│   │   │   │   └── page.tsx
│   │   │   ├── events/
│   │   │   │   └── page.tsx
│   │   │   ├── shopping-list/
│   │   │   │   └── page.tsx
│   │   │   ├── members/
│   │   │   │   └── page.tsx
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...betterauth]/
│   │   │           └── route.ts
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/           # Shadcn components
│   │   ├── forms/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   ├── AvailabilityForm.tsx
│   │   │   └── ReportForm.tsx
│   │   ├── planning/
│   │   │   ├── PlanningCalendar.tsx
│   │   │   ├── PlanningGenerator.tsx
│   │   │   └── AssignmentCard.tsx
│   │   ├── calendar/
│   │   │   └── AvailabilityCalendar.tsx
│   │   └── shared/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── NotificationBell.tsx
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── auth.ts
│   │   ├── socket.ts
│   │   ├── utils.ts
│   │   └── validators.ts
│   ├── hooks/
│   │   ├── use-planning.ts
│   │   ├── use-members.ts
│   │   ├── use-availabilities.ts
│   │   ├── use-notifications.ts
│   │   └── use-realtime.ts
│   ├── stores/
│   │   ├── notification-store.ts
│   │   └── ui-store.ts
│   ├── types/
│   │   ├── index.ts
│   │   ├── api.ts
│   │   └── models.ts
│   └── styles/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── public/
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── Dockerfile

# Infrastructure
docker-compose.yml          # Développement local
docker-compose.prod.yml     # Production
.github/
├── workflows/
│   ├── frontend-ci.yml
│   ├── frontend-deploy.yml
│   ├── backend-ci.yml
│   └── backend-deploy.yml
└── dependabot.yml
```

**Structure Decision**: Architecture web application avec frontend Next.js et backend FastAPI séparés. Cette structure permet un déploiement indépendant (Vercel pour frontend, Dokploy pour backend), une scalabilité horizontale, et une séparation claire des responsabilités.

## Complexity Tracking

> Aucune violation de la constitution - section vide.

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A       | N/A        | N/A                                  |
