# Deployment Guide

> Guide complet pour le déploiement de MonService - Church Team Management SaaS

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture de déploiement](#architecture-de-déploiement)
- [Backend - Dokploy](#backend---dokploy)
- [Frontend - Vercel](#frontend---vercel)
- [Variables d'environnement](#variables-denvironnement)
- [Migrations de base de données](#migrations-de-base-de-données)
- [Procédures de rollback](#procédures-de-rollback)
- [Checklist de déploiement](#checklist-de-déploiement)
- [Monitoring et alertes](#monitoring-et-alertes)

---

## Vue d'ensemble

MonService utilise une architecture découplée avec :

| Composant           | Plateforme                  | URL Production                 |
| ------------------- | --------------------------- | ------------------------------ |
| **Frontend**        | Vercel                      | `https://monservice.app`       |
| **Backend API**     | Dokploy (Docker)            | `https://api.monservice.app`   |
| **Base de données** | PostgreSQL 15+              | Hetzner Cloud / Managed DB     |
| **Cache/Queue**     | Redis 7+                    | Hetzner Cloud                  |
| **File Storage**    | Hetzner Object Storage (S3) | `https://files.monservice.app` |

---

## Architecture de déploiement

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
          ▼                                       ▼
┌─────────────────────┐              ┌─────────────────────┐
│      VERCEL         │              │      DOKPLOY        │
│  (Frontend Next.js) │              │   (Backend FastAPI) │
│                     │              │                     │
│  - Edge Runtime     │    REST/WS   │  - Docker Container │
│  - Static Assets    │◄────────────►│  - Celery Workers   │
│  - ISR/SSR          │              │  - WebSocket Server │
└─────────────────────┘              └─────────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
                    ▼                         ▼                         ▼
          ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
          │   PostgreSQL    │      │     Redis       │      │   S3 Storage    │
          │   (Database)    │      │  (Cache/Queue)  │      │    (Files)      │
          └─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## Backend - Dokploy

### Prérequis

- Serveur avec Docker installé
- Dokploy installé et configuré
- Accès SSH au serveur
- Domaine configuré (`api.monservice.app`)

### Configuration Dokploy

#### 1. Créer un nouveau projet

```bash
# Via l'interface Dokploy ou CLI
dokploy project create monservice-backend
```

#### 2. Configurer le Dockerfile

Le backend utilise un Dockerfile multi-stage pour optimiser la taille de l'image :

```dockerfile
# backend/Dockerfile
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for fast package management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system --compile-bytecode .

FROM python:3.13-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

# Create non-root user
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 3. Docker Compose pour production

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - APP_ENV=production
      - DEBUG=false
    ports:
      - "8000:8000"
    restart: unless-stopped
    depends_on:
      - postgres
      - redis

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.worker worker --loglevel=info --concurrency=4
    environment:
      - APP_ENV=production
    restart: unless-stopped
    depends_on:
      - redis

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.worker beat --loglevel=info
    environment:
      - APP_ENV=production
    restart: unless-stopped
    depends_on:
      - redis
```

#### 4. Configuration Dokploy

Dans l'interface Dokploy :

1. **Source** : GitHub repository `regi-gouale/mon-service`
2. **Branch** : `main`
3. **Build Path** : `backend/`
4. **Dockerfile** : `Dockerfile`
5. **Port** : `8000`
6. **Domain** : `api.monservice.app`
7. **SSL** : Let's Encrypt (auto)

#### 5. Hooks de déploiement

```bash
# Pre-deploy hook (dans Dokploy)
cd /app && alembic upgrade head

# Post-deploy hook
curl -X POST https://api.monservice.app/health
```

---

## Frontend - Vercel

### Configuration initiale

#### 1. Connexion du repository

1. Aller sur [vercel.com](https://vercel.com)
2. Importer le repository `regi-gouale/mon-service`
3. Configurer le root directory : `frontend`

#### 2. Configuration du projet

Dans **Project Settings** :

| Paramètre        | Valeur                           |
| ---------------- | -------------------------------- |
| Framework Preset | Next.js                          |
| Root Directory   | `frontend`                       |
| Build Command    | `pnpm build`                     |
| Output Directory | `.next`                          |
| Install Command  | `pnpm install --frozen-lockfile` |
| Node.js Version  | 20.x                             |

#### 3. vercel.json

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "pnpm build",
  "installCommand": "pnpm install --frozen-lockfile",
  "framework": "nextjs",
  "regions": ["cdg1"],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [{ "key": "Cache-Control", "value": "no-store, max-age=0" }]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

#### 4. Domaines

| Environnement | Domaine                  |
| ------------- | ------------------------ |
| Production    | `monservice.app`         |
| Preview       | `preview.monservice.app` |
| Development   | `dev.monservice.app`     |

---

## Variables d'environnement

### Backend (Dokploy)

#### Production

```bash
# Application
APP_NAME="Church Team Management API"
APP_ENV=production
DEBUG=false
API_V1_PREFIX=/api/v1

# Security (IMPORTANT: générer avec `openssl rand -hex 32`)
SECRET_KEY=<generated-secret-key>

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false

# Database
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/monservice_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://redis-host:6379/0
REDIS_MAX_CONNECTIONS=50

# Celery
CELERY_BROKER_URL=redis://redis-host:6379/1
CELERY_RESULT_BACKEND=redis://redis-host:6379/2
CELERY_TASK_ALWAYS_EAGER=false
CELERY_TASK_TIME_LIMIT=300

# JWT
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth2
GOOGLE_CLIENT_ID=<production-google-client-id>
GOOGLE_CLIENT_SECRET=<production-google-client-secret>
GOOGLE_REDIRECT_URI=https://monservice.app/api/auth/callback/google

# Email (Production SMTP)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
SMTP_TLS=true
SMTP_FROM_NAME="MonService"
SMTP_FROM_EMAIL=noreply@monservice.app

# S3 Storage (Hetzner Object Storage)
S3_ENDPOINT_URL=https://fsn1.your-objectstorage.com
S3_ACCESS_KEY=<access-key>
S3_SECRET_KEY=<secret-key>
S3_BUCKET_NAME=monservice-prod
S3_REGION=fsn1
S3_USE_SSL=true

# CORS
CORS_ORIGINS=https://monservice.app,https://www.monservice.app
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_AUTH_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Sentry
SENTRY_DSN=https://xxx@sentry.io/xxx
SENTRY_ENVIRONMENT=production

# Feature Flags
FEATURE_OAUTH_GOOGLE=true
FEATURE_WEBSOCKETS=true
FEATURE_EMAIL_NOTIFICATIONS=true
```

#### Staging

```bash
APP_ENV=staging
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/monservice_staging
CORS_ORIGINS=https://staging.monservice.app
SENTRY_ENVIRONMENT=staging
```

### Frontend (Vercel)

#### Production

```bash
NEXT_PUBLIC_API_URL=https://api.monservice.app
NEXT_PUBLIC_WS_URL=wss://api.monservice.app
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx

# Auth
BETTER_AUTH_SECRET=<generated-secret>
BETTER_AUTH_URL=https://monservice.app

# Analytics (optionnel)
NEXT_PUBLIC_POSTHOG_KEY=<posthog-key>
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

#### Preview (branches de PR)

```bash
NEXT_PUBLIC_API_URL=https://api-staging.monservice.app
NEXT_PUBLIC_APP_ENV=preview
```

---

## Migrations de base de données

### Stratégie de migration

1. **Toujours** exécuter les migrations avant le déploiement du code
2. Les migrations doivent être **réversibles** (down migrations)
3. Utiliser des migrations **non-breaking** quand possible

### Exécution en production

#### Via Dokploy (pre-deploy hook)

```bash
# Exécuté automatiquement avant chaque déploiement
alembic upgrade head
```

#### Manuellement (SSH)

```bash
# Se connecter au container
docker exec -it monservice-api bash

# Vérifier le statut
alembic current
alembic history

# Appliquer les migrations
alembic upgrade head

# Ou une migration spécifique
alembic upgrade abc123
```

### Migrations non-breaking

Pour les changements de schéma majeurs, utiliser une approche en plusieurs étapes :

```
1. Déploiement 1: Ajouter nouvelle colonne (nullable)
2. Déploiement 2: Code utilise les deux colonnes
3. Déploiement 3: Migrer les données
4. Déploiement 4: Supprimer l'ancienne colonne
```

### Bonnes pratiques

```python
# migrations/versions/xxx_add_user_phone.py

def upgrade():
    # ✅ Non-breaking: colonne nullable avec défaut
    op.add_column('users',
        sa.Column('phone', sa.String(20), nullable=True, server_default=None)
    )

def downgrade():
    op.drop_column('users', 'phone')
```

---

## Procédures de rollback

### Rollback Backend (Dokploy)

#### 1. Rollback rapide (même image)

```bash
# Via Dokploy UI
# Settings > Deployments > Select previous deployment > Rollback

# Ou via CLI
dokploy rollback monservice-backend --to <deployment-id>
```

#### 2. Rollback avec migration

```bash
# 1. Se connecter au serveur
ssh user@server

# 2. Identifier la migration cible
docker exec monservice-api alembic history

# 3. Rollback la migration
docker exec monservice-api alembic downgrade -1  # Une migration
docker exec monservice-api alembic downgrade abc123  # Migration spécifique

# 4. Rollback l'application
dokploy rollback monservice-backend --to <previous-deployment>
```

#### 3. Rollback d'urgence

```bash
# Stopper le service immédiatement
docker stop monservice-api

# Démarrer l'ancienne version
docker run -d --name monservice-api-rollback \
  --env-file .env.production \
  -p 8000:8000 \
  monservice-api:<previous-tag>
```

### Rollback Frontend (Vercel)

#### Via Dashboard

1. Aller sur **Vercel Dashboard** > **Deployments**
2. Trouver le déploiement précédent (stable)
3. Cliquer sur **...** > **Promote to Production**

#### Via CLI

```bash
# Lister les déploiements
vercel ls

# Promouvoir un déploiement spécifique
vercel promote <deployment-url> --prod
```

### Rollback de base de données

⚠️ **ATTENTION** : Sauvegarder avant tout rollback de DB !

```bash
# 1. Créer un backup
pg_dump -h db-host -U user monservice_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Rollback une migration
docker exec monservice-api alembic downgrade -1

# 3. Si nécessaire, restaurer le backup
psql -h db-host -U user monservice_prod < backup_20241227_120000.sql
```

---

## Checklist de déploiement

### Avant le déploiement

- [ ] Tests passent en CI (backend + frontend)
- [ ] Lint et type checking OK
- [ ] Code review approuvé
- [ ] Migrations testées localement
- [ ] Variables d'environnement mises à jour si nécessaire
- [ ] Documentation mise à jour si besoin
- [ ] Backup de la base de données effectué

### Pendant le déploiement

- [ ] Vérifier les logs Dokploy/Vercel
- [ ] Confirmer que les migrations ont été appliquées
- [ ] Vérifier le health check de l'API
- [ ] Tester les endpoints critiques manuellement

### Après le déploiement

- [ ] Vérifier les dashboards de monitoring
- [ ] Confirmer absence d'erreurs dans Sentry
- [ ] Tester le flow utilisateur principal
- [ ] Vérifier les performances (latence API)
- [ ] Notifier l'équipe du déploiement réussi

### En cas de problème

1. **Évaluer la sévérité** (P0-P3)
2. **P0/P1** : Rollback immédiat
3. **P2/P3** : Hotfix possible
4. **Documenter** l'incident dans le post-mortem

---

## Monitoring et alertes

### Métriques à surveiller

| Métrique           | Seuil d'alerte | Action        |
| ------------------ | -------------- | ------------- |
| API latency p95    | > 500ms        | Investigate   |
| API latency p99    | > 1000ms       | Alert         |
| Error rate         | > 1%           | Alert         |
| CPU usage          | > 80%          | Scale up      |
| Memory usage       | > 85%          | Investigate   |
| DB connections     | > 80% pool     | Alert         |
| Celery queue depth | > 100          | Scale workers |

### Outils recommandés

- **Error Tracking** : Sentry
- **Logs** : Dokploy logs / Vercel logs
- **Metrics** : Prometheus + Grafana (optionnel)
- **Uptime** : UptimeRobot / Better Stack

### Configuration Sentry

```python
# backend/app/core/config.py
import sentry_sdk

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=0.1,  # 10% des transactions
        profiles_sample_rate=0.1,
    )
```

---

## Contacts et escalade

| Rôle            | Contact             | Quand contacter              |
| --------------- | ------------------- | ---------------------------- |
| Lead Dev        | @regi-gouale        | Problèmes techniques majeurs |
| DevOps          | -                   | Infrastructure down          |
| Support Dokploy | support@dokploy.com | Problèmes plateforme         |
| Support Vercel  | support@vercel.com  | Problèmes frontend           |

---

## Historique des déploiements

Maintenir un changelog des déploiements majeurs :

```markdown
## 2025-01-15 - v1.0.0

- Initial production release
- Features: Auth, Availability, Planning

## 2025-01-20 - v1.1.0

- Added: Notifications system
- Fixed: Planning generation performance
```
