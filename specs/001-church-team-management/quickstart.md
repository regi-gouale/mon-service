# Quickstart - Church Team Management

Guide de démarrage rapide pour le développement local.

---

## Prérequis

- **Node.js** 20+ (LTS)
- **Python** 3.11+
- **Docker** & Docker Compose
- **pnpm** 9+ (frontend)
- **uv** ou **pip** (backend)
- **Make** (optionnel, recommandé)

---

## 1. Cloner et configurer

```bash
# Cloner le repository
git clone https://github.com/votre-org/mon-service.git
cd mon-service

# Copier les fichiers d'environnement
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

---

## 2. Configuration des variables d'environnement

### Backend (`backend/.env`)

```env
# Application
APP_NAME=MonService
APP_ENV=development
DEBUG=true
SECRET_KEY=your-super-secret-key-min-32-chars

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/monservice
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# S3 Storage (Hetzner Object Storage)
S3_ENDPOINT_URL=https://fsn1.your-objectstorage.com
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=monservice-dev
S3_REGION=fsn1

# Email (SMTP)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
MAIL_FROM=noreply@monservice.local

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Sentry (optionnel)
SENTRY_DSN=
```

### Frontend (`frontend/.env.local`)

```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Better Auth
BETTER_AUTH_SECRET=your-better-auth-secret-min-32-chars
BETTER_AUTH_URL=http://localhost:3000

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false

# Sentry (optionnel)
NEXT_PUBLIC_SENTRY_DSN=
```

---

## 3. Démarrer les services avec Docker

### Option A: Tout avec Docker (recommandé pour démarrer)

```bash
# Démarrer tous les services
docker compose up -d

# Vérifier les logs
docker compose logs -f
```

### Option B: Services infra uniquement (pour développement actif)

```bash
# Démarrer uniquement PostgreSQL, Redis, et MailHog
docker compose up -d postgres redis mailhog
```

### Docker Compose (`docker-compose.yml`)

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:15-alpine
    container_name: monservice-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: monservice
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: monservice-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  mailhog:
    image: mailhog/mailhog:v1.0.1
    container_name: monservice-mailhog
    ports:
      - "1025:1025" # SMTP
      - "8025:8025" # Web UI
    logging:
      driver: none

  # Optionnel: MinIO pour simuler S3 en local
  minio:
    image: minio/minio:latest
    container_name: monservice-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000" # API
      - "9001:9001" # Console
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

---

## 4. Backend Setup

```bash
cd backend

# Créer l'environnement virtuel (avec uv - recommandé)
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Installer les dépendances
uv pip install -r requirements.txt
# ou avec pip: pip install -r requirements.txt

# Installer les dépendances de développement
uv pip install -r requirements-dev.txt

# Appliquer les migrations
alembic upgrade head

# Seed des données de test (optionnel)
python -m app.scripts.seed_dev

# Lancer le serveur de développement
uvicorn app.main:app --reload --port 8000
```

### Commandes Makefile (Backend)

```makefile
# Makefile
.PHONY: dev test lint migrate

dev:
	uvicorn app.main:app --reload --port 8000

test:
	pytest --cov=app --cov-report=html

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

lint:
	ruff check app tests
	mypy app

format:
	ruff format app tests

migrate:
	alembic upgrade head

migrate-new:
	alembic revision --autogenerate -m "$(name)"

celery:
	celery -A app.worker worker --loglevel=info

celery-beat:
	celery -A app.worker beat --loglevel=info
```

---

## 5. Frontend Setup

```bash
cd frontend

# Installer les dépendances
pnpm install

# Lancer le serveur de développement
pnpm dev
```

### Scripts disponibles (Frontend)

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint && tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "format": "prettier --write .",
    "check": "pnpm lint && pnpm test"
  }
}
```

---

## 6. URLs de développement

| Service       | URL                         | Description                  |
| ------------- | --------------------------- | ---------------------------- |
| Frontend      | http://localhost:3000       | Application Next.js          |
| Backend API   | http://localhost:8000       | API FastAPI                  |
| API Docs      | http://localhost:8000/docs  | Swagger UI                   |
| ReDoc         | http://localhost:8000/redoc | Documentation ReDoc          |
| MailHog       | http://localhost:8025       | Inbox emails de test         |
| MinIO Console | http://localhost:9001       | Gestion S3 local             |
| pgAdmin       | http://localhost:5050       | Admin PostgreSQL (optionnel) |

---

## 7. Workflow de développement

### Créer une nouvelle branche

```bash
git checkout -b feature/ma-fonctionnalite
```

### Lancer les tests

```bash
# Backend
cd backend && make test

# Frontend
cd frontend && pnpm test
```

### Vérifier le code avant commit

```bash
# Backend
cd backend && make lint

# Frontend
cd frontend && pnpm lint
```

### Créer une migration de base de données

```bash
cd backend

# Modifier les modèles SQLAlchemy dans app/models/
# Puis générer la migration:
make migrate-new name="add_user_preferences"

# Appliquer la migration
make migrate
```

---

## 8. Debugging

### Logs structurés

```bash
# Backend avec logs JSON
LOG_FORMAT=json uvicorn app.main:app --reload

# Voir les logs Celery
docker compose logs -f celery
```

### Debugger Python (VS Code)

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

### Debugger TypeScript (VS Code)

Utiliser les Chrome DevTools via `next dev` (port 3000).

---

## 9. Troubleshooting

### Port déjà utilisé

```bash
# Trouver le processus
lsof -i :8000

# Tuer le processus
kill -9 <PID>
```

### Reset complet de la base de données

```bash
# Supprimer et recréer
docker compose down -v
docker compose up -d postgres redis
cd backend && alembic upgrade head && python -m app.scripts.seed_dev
```

### Problème de cache Redis

```bash
docker compose exec redis redis-cli FLUSHALL
```

### Nettoyer les conteneurs Docker

```bash
docker compose down -v --remove-orphans
docker system prune -f
```

---

## 10. Extensions VS Code recommandées

```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "prisma.prisma",
    "ms-azuretools.vscode-docker"
  ]
}
```

---

## Contact & Support

- **Slack**: #dev-monservice
- **Documentation**: [docs.monservice.com](https://docs.monservice.com)
- **Issues**: GitHub Issues
