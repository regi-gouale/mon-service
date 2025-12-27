# Church Team Management SaaS - Backend API

Backend FastAPI pour le système de gestion d'équipes d'église.

## Stack Technique

- **Framework** : FastAPI 0.127.1+
- **Serveur ASGI** : Uvicorn
- **Python** : 3.13+
- **Base de données** : PostgreSQL 15+ (SQLAlchemy 2.0 async)
- **Validations** : Pydantic v2
- **Migrations** : Alembic
- **Type checking** : MyPy (strict mode)
- **Testing** : pytest + pytest-asyncio (coverage ≥ 80%)
- **Linting** : ruff + mypy
- **Package manager** : uv (ultra-fast Python package installer)

## Installation

### Prérequis

- Python 3.13+ (uv installera la bonne version automatiquement)
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (pour les services locaux)

### Setup Local

```bash
# 1. Démarrer les services Docker
make docker-up

# 2. Installer les dépendances (backend + dev)
make install-backend

# ou manuellement:
# cd backend
# uv sync --all-groups

# 3. Créer le fichier .env
cp .env.example .env

# 4. Appliquer les migrations
make db-upgrade

# 5. Charger les données de test (optionnel)
make db-seed
```

## Développement

### Démarrer le serveur

```bash
make dev-backend

# ou manuellement:
# cd backend && uv run uvicorn app.main:app --reload
```

Le serveur démarre sur `http://localhost:8000`

### Documentation API

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI Schema** : http://localhost:8000/openapi.json

### Tests

```bash
# Tous les tests
make test-backend

# Tests unitaires uniquement
make test-backend-unit

# Tests d'intégration
make test-backend-integration

# Tests avec couverture
make test-cov
```

### Linting & Formatting

```bash
# Lint le backend
make lint-backend

# Formate le code
make format-backend

# Exécute tous les pre-commit hooks
make hooks-run
```

## Structure du Projet

```
backend/
├── app/
│   ├── api/v1/              # Routes versionnées
│   │   └── routes/
│   ├── core/                # Configuration et setup
│   │   ├── config.py        # Pydantic Settings
│   │   ├── database.py      # SQLAlchemy async
│   │   └── security.py      # JWT, hashing, etc.
│   ├── domain/              # Entities et Value Objects
│   ├── models/              # SQLAlchemy ORM models
│   ├── repositories/        # Data access layer
│   ├── schemas/             # Pydantic schemas (request/response)
│   ├── services/            # Business logic
│   ├── websockets/          # WebSocket handlers
│   ├── workers/             # Celery tasks
│   └── main.py              # Application entry point
├── migrations/              # Alembic migrations
├── tests/
│   ├── contract/            # Contract tests
│   ├── integration/         # Integration tests
│   └── unit/                # Unit tests
├── pyproject.toml           # Project config & dependencies
├── .python-version          # Python version (3.13)
└── uv.lock                  # Locked dependencies
```

## Commandes Principales

| Commande              | Description                     |
| --------------------- | ------------------------------- |
| `make install`        | Installe toutes les dépendances |
| `make dev-backend`    | Démarre le serveur en mode dev  |
| `make test-backend`   | Lance tous les tests            |
| `make lint-backend`   | Lint le code Python             |
| `make format-backend` | Formate le code                 |
| `make db-migrate`     | Crée une nouvelle migration     |
| `make db-upgrade`     | Applique les migrations         |
| `make db-reset`       | Réinitialise la BD              |
| `make hooks-run`      | Exécute les pre-commit hooks    |

## Configuration Environnement

Voir [.env.example](.env.example) pour toutes les variables disponibles.

Variables importantes :

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/church_team_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (SMTP)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SEND_FROM_EMAIL=noreply@churchteam.local

# S3/Object Storage
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=church-team
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
```

## Architecture

### Clean Architecture (Hexagonal)

- **Routes** → **Services** → **Repositories** → **Database**
- Pas de logique métier dans les routes
- Services isolent la logique métier
- Repositories gèrent l'accès aux données

### Async/Await

Tout le code est asynchrone pour la performance :

```python
@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user = await user_repository.get_by_id(user_id)
    return user
```

## Sécurité

- **JWT** avec refresh tokens (15min/7days)
- **Bcrypt** pour les passwords
- **CORS** configuré
- **Rate limiting** sur les endpoints sensibles
- **Validation** client + serveur (Pydantic)

## Performance

- **Cache Redis** pour les données fréquentes
- **Async/await** partout
- **Database indexes** sur les clés étrangères
- **Lazy loading** des relations
- **Monitoring** avec logs JSON structurés

## CI/CD

Workflows GitHub Actions :

- Linting (ruff, mypy) sur chaque PR
- Tests (pytest) sur chaque PR
- Coverage reports (Codecov)

Voir [.github/workflows/]() pour les détails.

## Dépannage

### "ModuleNotFoundError: No module named 'app'"

```bash
# Assurez-vous d'être dans le dossier backend
cd backend
uv sync --all-groups
```

### "Connection refused" (PostgreSQL)

```bash
# Vérifiez que Docker est en marche
make docker-ps
make docker-logs-postgres
```

### "Port 8000 already in use"

```bash
# Trouvez le processus qui utilise le port
lsof -i :8000
# Tuez-le
kill -9 <PID>
```

## Ressources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [uv Documentation](https://docs.astral.sh/uv/)

## License

Proprietary - Church Team Management SaaS
