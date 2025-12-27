# MonService - Church Team Management SaaS

[![Backend Tests](https://github.com/regi-gouale/mon-service/actions/workflows/test-backend.yml/badge.svg)](https://github.com/regi-gouale/mon-service/actions/workflows/test-backend.yml)
[![Frontend Tests](https://github.com/regi-gouale/mon-service/actions/workflows/test-frontend.yml/badge.svg)](https://github.com/regi-gouale/mon-service/actions/workflows/test-frontend.yml)
[![codecov](https://codecov.io/gh/regi-gouale/mon-service/graph/badge.svg)](https://codecov.io/gh/regi-gouale/mon-service)

SaaS de gestion d'équipes pour les départements d'église permettant d'organiser les plannings, la communication et la logistique des services et événements.

## 🚀 Fonctionnalités

- **Authentification sécurisée** (email/password + OAuth Google)
- **Gestion des indisponibilités** par les membres
- **Génération automatique de plannings** avec algorithme d'équité
- **Notifications temps réel** (WebSockets) et par email
- **Gestion des codes vestimentaires**, inventaire, rapports de service
- **Multi-tenancy** avec isolation par organisation

## 📁 Structure du projet

```
mon-service/
├── backend/                 # API FastAPI (Python 3.13+)
│   ├── app/
│   │   ├── api/v1/routes/  # Endpoints API
│   │   ├── core/           # Configuration, sécurité
│   │   ├── domain/         # Entités et value objects
│   │   ├── models/         # Modèles SQLAlchemy
│   │   ├── repositories/   # Couche d'accès aux données
│   │   ├── schemas/        # Schémas Pydantic
│   │   ├── services/       # Logique métier
│   │   ├── workers/        # Tâches Celery
│   │   └── websockets/     # Communication temps réel
│   ├── migrations/         # Migrations Alembic
│   └── tests/              # Tests unitaires, intégration, contract
│
├── frontend/               # Application Next.js (TypeScript)
│   ├── app/               # App Router (pages, layouts)
│   ├── components/        # Composants React
│   ├── hooks/             # Custom hooks
│   ├── lib/               # Utilitaires, API client
│   ├── stores/            # Zustand stores
│   ├── types/             # Types TypeScript
│   └── tests/             # Tests frontend
│
├── specs/                  # Spécifications et documentation
├── docs/                   # Documentation utilisateur
└── scripts/                # Scripts utilitaires
```

## 🛠 Stack technique

### Backend

- **Python 3.13** avec type hints stricts
- **FastAPI** - Framework web async
- **SQLAlchemy 2.0** - ORM async
- **Pydantic v2** - Validation des données
- **Celery** - Tâches asynchrones
- **PostgreSQL 15+** - Base de données
- **Redis 7+** - Cache et broker

### Frontend

- **Next.js 14+** - Framework React (App Router)
- **TypeScript** - Typage strict
- **TailwindCSS** - Styling
- **Shadcn/ui** - Composants UI
- **TanStack Query** - Gestion du cache API
- **Zustand** - State management
- **Better Auth** - Authentification

## 🚦 Démarrage rapide

### Prérequis

- Node.js 20+ (LTS)
- Python 3.13
- Docker & Docker Compose
- pnpm 9+
- uv (ou pip)

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/regi-gouale/mon-service.git
cd mon-service

# 2. Copier les fichiers d'environnement
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Démarrer les services Docker (PostgreSQL, Redis, Mailpit, MinIO)
docker compose up -d

# 4. Setup Backend
cd backend
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 5. Setup Frontend (dans un autre terminal)
cd frontend
pnpm install
pnpm dev
```

### URLs de développement

| Service     | URL                        | Description         |
| ----------- | -------------------------- | ------------------- |
| Frontend    | http://localhost:3000      | Application Next.js |
| Backend API | http://localhost:8000      | API FastAPI         |
| API Docs    | http://localhost:8000/docs | Swagger UI          |
| Mailpit     | http://localhost:8025      | Emails de test      |
| MinIO       | http://localhost:9001      | Console S3          |

## 📝 Documentation

- [Quickstart détaillé](specs/001-church-team-management/quickstart.md)
- [Spécification fonctionnelle](specs/001-church-team-management/spec.md)
- [Modèle de données](specs/001-church-team-management/data-model.md)
- [Plan d'implémentation](specs/001-church-team-management/plan.md)
- [API OpenAPI](specs/001-church-team-management/contracts/openapi.yaml)

## 🧪 Tests

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html

# Frontend
cd frontend
pnpm test
```

## 📄 Licence

Ce projet est sous licence privée.

---

Fait avec ❤️ pour les églises
