# =============================================================================
# Church Team Management SaaS - Makefile
# =============================================================================
# Commandes unifiées pour le développement du monorepo
# Usage: make <commande>
# =============================================================================

.PHONY: help install install-backend install-frontend \
        dev dev-backend dev-frontend \
        docker-up docker-down docker-logs docker-ps docker-clean \
        db-migrate db-upgrade db-downgrade db-reset db-seed \
        test test-backend test-frontend test-e2e test-cov \
        lint lint-backend lint-frontend format \
        build build-backend build-frontend \
        clean clean-backend clean-frontend clean-all

# =============================================================================
# Variables
# =============================================================================
DOCKER_COMPOSE = docker compose
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# Couleurs pour l'affichage
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

# =============================================================================
# Aide
# =============================================================================
help: ## Affiche cette aide
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Church Team Management SaaS - Commandes disponibles$(NC)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================
install: install-backend install-frontend ## Installe toutes les dépendances

install-backend: ## Installe les dépendances backend (Python/uv)
	@echo "$(BLUE)📦 Installation des dépendances backend...$(NC)"
	cd $(BACKEND_DIR) && uv sync --all-groups
	@echo "$(GREEN)✅ Dépendances backend installées$(NC)"

install-frontend: ## Installe les dépendances frontend (pnpm)
	@echo "$(BLUE)📦 Installation des dépendances frontend...$(NC)"
	cd $(FRONTEND_DIR) && pnpm install
	@echo "$(GREEN)✅ Dépendances frontend installées$(NC)"

# =============================================================================
# Développement
# =============================================================================
dev: docker-up ## Lance l'environnement de développement complet
	@echo "$(BLUE)🚀 Démarrage de l'environnement de développement...$(NC)"
	@echo "$(YELLOW)Utilisez 'make dev-backend' et 'make dev-frontend' dans des terminaux séparés$(NC)"

dev-backend: ## Lance le serveur backend (FastAPI avec hot-reload)
	@echo "$(BLUE)🐍 Démarrage du backend FastAPI...$(NC)"
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Lance le serveur frontend (Next.js avec hot-reload)
	@echo "$(BLUE)⚛️  Démarrage du frontend Next.js...$(NC)"
	cd $(FRONTEND_DIR) && pnpm dev

dev-all: docker-up ## Lance backend et frontend en parallèle (nécessite tmux ou similar)
	@echo "$(BLUE)🚀 Démarrage de tous les services...$(NC)"
	@make -j2 dev-backend dev-frontend

# =============================================================================
# Docker
# =============================================================================
docker-up: ## Démarre les services Docker (PostgreSQL, Redis, Mailpit, MinIO)
	@echo "$(BLUE)🐳 Démarrage des services Docker...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Services Docker démarrés$(NC)"
	@echo ""
	@echo "$(YELLOW)Services disponibles:$(NC)"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Mailpit UI: http://localhost:8025"
	@echo "  - MinIO Console: http://localhost:9001"

docker-down: ## Arrête les services Docker
	@echo "$(BLUE)🐳 Arrêt des services Docker...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Services Docker arrêtés$(NC)"

docker-stop: ## Arrête les services Docker sans supprimer les conteneurs
	@echo "$(BLUE)🐳 Arrêt des conteneurs Docker...$(NC)"
	$(DOCKER_COMPOSE) stop
	@echo "$(GREEN)✅ Conteneurs Docker arrêtés$(NC)"

docker-restart: docker-down docker-up ## Redémarre les services Docker

docker-logs: ## Affiche les logs des services Docker
	$(DOCKER_COMPOSE) logs -f

docker-logs-postgres: ## Affiche les logs PostgreSQL
	$(DOCKER_COMPOSE) logs -f postgres

docker-logs-redis: ## Affiche les logs Redis
	$(DOCKER_COMPOSE) logs -f redis

docker-ps: ## Affiche l'état des services Docker
	$(DOCKER_COMPOSE) ps

docker-clean: ## Supprime les conteneurs et volumes Docker
	@echo "$(RED)⚠️  Suppression des conteneurs et volumes Docker...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	@echo "$(GREEN)✅ Conteneurs et volumes supprimés$(NC)"

# =============================================================================
# Base de données
# =============================================================================
db-migrate: ## Crée une nouvelle migration Alembic
	@read -p "Nom de la migration: " name; \
	cd $(BACKEND_DIR) && uv run alembic revision --autogenerate -m "$$name"

db-upgrade: ## Applique toutes les migrations
	@echo "$(BLUE)📊 Application des migrations...$(NC)"
	cd $(BACKEND_DIR) && uv run alembic upgrade head
	@echo "$(GREEN)✅ Migrations appliquées$(NC)"

db-downgrade: ## Annule la dernière migration
	@echo "$(YELLOW)⏪ Annulation de la dernière migration...$(NC)"
	cd $(BACKEND_DIR) && uv run alembic downgrade -1

db-reset: ## Réinitialise la base de données (supprime et recrée)
	@echo "$(RED)⚠️  Réinitialisation de la base de données...$(NC)"
	$(DOCKER_COMPOSE) down -v postgres
	$(DOCKER_COMPOSE) up -d postgres
	@echo "$(YELLOW)⏳ Attente du démarrage de PostgreSQL...$(NC)"
	@sleep 5
	cd $(BACKEND_DIR) && uv run alembic upgrade head
	@echo "$(GREEN)✅ Base de données réinitialisée$(NC)"

db-seed: ## Charge les données de test
	@echo "$(BLUE)🌱 Chargement des données de test...$(NC)"
	cd $(BACKEND_DIR) && uv run python -m scripts.seed
	@echo "$(GREEN)✅ Données de test chargées$(NC)"

db-shell: ## Ouvre un shell psql
	$(DOCKER_COMPOSE) exec postgres psql -U church_team -d church_team_db

# =============================================================================
# Tests
# =============================================================================
test: test-backend test-frontend ## Lance tous les tests

test-backend: ## Lance les tests backend (pytest)
	@echo "$(BLUE)🧪 Exécution des tests backend...$(NC)"
	cd $(BACKEND_DIR) && uv run pytest

test-backend-unit: ## Lance les tests unitaires backend
	@echo "$(BLUE)🧪 Exécution des tests unitaires backend...$(NC)"
	cd $(BACKEND_DIR) && uv run pytest tests/unit -v

test-backend-integration: ## Lance les tests d'intégration backend
	@echo "$(BLUE)🧪 Exécution des tests d'intégration backend...$(NC)"
	cd $(BACKEND_DIR) && uv run pytest tests/integration -v

test-frontend: ## Lance les tests frontend (Vitest)
	@echo "$(BLUE)🧪 Exécution des tests frontend...$(NC)"
	cd $(FRONTEND_DIR) && pnpm test

test-e2e: ## Lance les tests end-to-end (Playwright)
	@echo "$(BLUE)🧪 Exécution des tests e2e...$(NC)"
	cd $(FRONTEND_DIR) && pnpm test:e2e

test-cov: ## Lance les tests avec couverture
	@echo "$(BLUE)🧪 Exécution des tests avec couverture...$(NC)"
	cd $(BACKEND_DIR) && uv run pytest --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)📊 Rapport de couverture: backend/htmlcov/index.html$(NC)"

test-watch: ## Lance les tests backend en mode watch
	cd $(BACKEND_DIR) && uv run pytest --watch

# =============================================================================
# Linting & Formatting
# =============================================================================
lint: lint-backend lint-frontend ## Lance le linting sur tout le projet

lint-backend: ## Lance ruff sur le backend
	@echo "$(BLUE)🔍 Linting backend...$(NC)"
	cd $(BACKEND_DIR) && uv run ruff check .
	cd $(BACKEND_DIR) && uv run mypy app

lint-frontend: ## Lance ESLint sur le frontend
	@echo "$(BLUE)🔍 Linting frontend...$(NC)"
	cd $(FRONTEND_DIR) && pnpm lint

format: ## Formate le code (backend + frontend)
	@echo "$(BLUE)✨ Formatage du code...$(NC)"
	cd $(BACKEND_DIR) && uv run ruff format .
	cd $(BACKEND_DIR) && uv run ruff check --fix .
	cd $(FRONTEND_DIR) && pnpm format 2>/dev/null || true
	@echo "$(GREEN)✅ Code formaté$(NC)"

format-backend: ## Formate le code backend
	@echo "$(BLUE)✨ Formatage du code backend...$(NC)"
	cd $(BACKEND_DIR) && uv run ruff format .
	cd $(BACKEND_DIR) && uv run ruff check --fix .

format-frontend: ## Formate le code frontend
	@echo "$(BLUE)✨ Formatage du code frontend...$(NC)"
	cd $(FRONTEND_DIR) && pnpm format 2>/dev/null || true

# =============================================================================
# Build
# =============================================================================
build: build-backend build-frontend ## Build tout le projet

build-backend: ## Build le backend (vérification des types)
	@echo "$(BLUE)🏗️  Build backend...$(NC)"
	cd $(BACKEND_DIR) && uv run mypy app
	@echo "$(GREEN)✅ Backend build OK$(NC)"

build-frontend: ## Build le frontend Next.js
	@echo "$(BLUE)🏗️  Build frontend...$(NC)"
	cd $(FRONTEND_DIR) && pnpm build
	@echo "$(GREEN)✅ Frontend build OK$(NC)"

# =============================================================================
# Nettoyage
# =============================================================================
clean: clean-backend clean-frontend ## Nettoie les fichiers générés

clean-backend: ## Nettoie les fichiers backend
	@echo "$(BLUE)🧹 Nettoyage backend...$(NC)"
	cd $(BACKEND_DIR) && rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

clean-frontend: ## Nettoie les fichiers frontend
	@echo "$(BLUE)🧹 Nettoyage frontend...$(NC)"
	cd $(FRONTEND_DIR) && rm -rf .next out node_modules/.cache

clean-all: clean docker-clean ## Nettoie tout (y compris Docker)
	@echo "$(GREEN)✅ Tout est nettoyé$(NC)"

# =============================================================================
# Utilitaires
# =============================================================================
check: ## Vérifie que tout est bien configuré
	@echo "$(BLUE)🔍 Vérification de la configuration...$(NC)"
	@echo ""
	@echo "$(YELLOW)Versions:$(NC)"
	@python3 --version 2>/dev/null || echo "  ❌ Python non trouvé"
	@uv --version 2>/dev/null || echo "  ❌ uv non trouvé"
	@node --version 2>/dev/null || echo "  ❌ Node.js non trouvé"
	@pnpm --version 2>/dev/null || echo "  ❌ pnpm non trouvé"
	@docker --version 2>/dev/null || echo "  ❌ Docker non trouvé"
	@echo ""
	@echo "$(YELLOW)Services Docker:$(NC)"
	@$(DOCKER_COMPOSE) ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "  ❌ Docker Compose non disponible"

setup: ## Configuration initiale du projet
	@echo "$(BLUE)🚀 Configuration initiale du projet...$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Copie des fichiers .env...$(NC)"
	@test -f $(BACKEND_DIR)/.env || (test -f $(BACKEND_DIR)/.env.example && cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env && echo "   ✅ backend/.env créé") || echo "   ⚠️  backend/.env.example non trouvé"
	@test -f $(FRONTEND_DIR)/.env.local || (test -f $(FRONTEND_DIR)/.env.example && cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env.local && echo "   ✅ frontend/.env.local créé") || echo "   ⚠️  frontend/.env.example non trouvé"
	@echo ""
	@echo "$(YELLOW)2. Installation des dépendances...$(NC)"
	@make install
	@echo ""
	@echo "$(YELLOW)3. Installation des pre-commit hooks...$(NC)"
	@make hooks-install
	@echo ""
	@echo "$(YELLOW)4. Démarrage des services Docker...$(NC)"
	@make docker-up
	@echo ""
	@echo "$(YELLOW)5. Application des migrations...$(NC)"
	@sleep 3
	@make db-upgrade 2>/dev/null || echo "   ⚠️  Migrations non disponibles (à configurer)"
	@echo ""
	@echo "$(GREEN)✅ Configuration terminée !$(NC)"
	@echo ""
	@echo "$(YELLOW)Prochaines étapes:$(NC)"
	@echo "  1. Ouvrez un terminal et lancez: make dev-backend"
	@echo "  2. Ouvrez un autre terminal et lancez: make dev-frontend"
	@echo "  3. Backend: http://localhost:8000/docs"
	@echo "  4. Frontend: http://localhost:3000"

# =============================================================================
# Pre-commit hooks
# =============================================================================
hooks-install: ## Installe les pre-commit hooks
	@echo "$(BLUE)🪝 Installation des pre-commit hooks...$(NC)"
	cd $(BACKEND_DIR) && uv run pre-commit install --install-hooks
	cd $(BACKEND_DIR) && uv run pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✅ Pre-commit hooks installés (pre-commit + commit-msg)$(NC)"

hooks-run: ## Exécute les pre-commit hooks sur tous les fichiers
	@echo "$(BLUE)🪝 Exécution des pre-commit hooks...$(NC)"
	cd $(BACKEND_DIR) && uv run pre-commit run --all-files

hooks-update: ## Met à jour les versions des pre-commit hooks
	@echo "$(BLUE)🔄 Mise à jour des pre-commit hooks...$(NC)"
	cd $(BACKEND_DIR) && uv run pre-commit autoupdate
	@echo "$(GREEN)✅ Pre-commit hooks mis à jour$(NC)"

hooks-uninstall: ## Désinstalle les pre-commit hooks
	@echo "$(YELLOW)⚠️  Désinstallation des pre-commit hooks...$(NC)"
	cd $(BACKEND_DIR) && uv run pre-commit uninstall
	cd $(BACKEND_DIR) && uv run pre-commit uninstall --hook-type commit-msg
	@echo "$(GREEN)✅ Pre-commit hooks désinstallés$(NC)"

# =============================================================================
# Celery (Workers)
# =============================================================================
worker: ## Lance le worker Celery
	@echo "$(BLUE)⚙️  Démarrage du worker Celery...$(NC)"
	cd $(BACKEND_DIR) && uv run celery -A app.workers.celery_app worker --loglevel=info

worker-beat: ## Lance le scheduler Celery Beat
	@echo "$(BLUE)⏰ Démarrage de Celery Beat...$(NC)"
	cd $(BACKEND_DIR) && uv run celery -A app.workers.celery_app beat --loglevel=info

flower: ## Lance Flower (monitoring Celery)
	@echo "$(BLUE)🌸 Démarrage de Flower...$(NC)"
	cd $(BACKEND_DIR) && uv run celery -A app.workers.celery_app flower --port=5555
