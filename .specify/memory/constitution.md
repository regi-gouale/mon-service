# <!--

# SYNC IMPACT REPORT

Version change: 0.0.0 → 1.0.0 (Initial constitution creation)

Modified principles: N/A (first version)

Added sections:

- Core Principles (7 principles)
  - I. Typage Strict & Stack Technique
  - II. Architecture & Séparation des Couches
  - III. Qualité & Tests (NON-NÉGOCIABLE)
  - IV. Sécurité (NON-NÉGOCIABLE)
  - V. Performance
  - VI. Expérience Développeur
  - VII. Conventions & Standards
- Stack Technique
- Workflow de Développement

Removed sections: N/A (first version)

Templates requiring updates:
✅ plan-template.md - Compatible (Constitution Check section exists)
✅ spec-template.md - Compatible (User stories + requirements structure)
✅ tasks-template.md - Compatible (Phase structure aligns with principles)

# Follow-up TODOs: None

-->

# Mon Service Constitution

## Core Principles

### I. Typage Strict & Stack Technique

Le typage strict est OBLIGATOIRE sur l'ensemble du projet :

**Frontend (Next.js 16+ / TypeScript)**

- TypeScript en mode `strict: true` dans `tsconfig.json`
- Aucun usage de `any` sans justification documentée dans le code
- App Router OBLIGATOIRE avec React Server Components par défaut
- Client Components (`"use client"`) uniquement quand l'interactivité le nécessite
- UI avec TailwindCSS et Shadcn UI exclusivement
- Authentification via Better Auth

**Backend (FastAPI / Python 3.12+)**

- Type hints Python OBLIGATOIRES sur toutes les fonctions, méthodes et paramètres
- Pydantic OBLIGATOIRE pour la validation de toutes les données entrantes/sortantes
- Async/await OBLIGATOIRE pour les opérations I/O
- Documentation OpenAPI générée automatiquement via FastAPI

**Base de données**

- PostgreSQL comme unique SGBD
- SQLAlchemy pour l'ORM avec typage strict
- Alembic pour toutes les migrations (jamais de modifications manuelles du schéma)

**Rationale** : Le typage strict prévient les erreurs à la compilation, améliore l'autocomplétion, et sert de documentation vivante.

### II. Architecture & Séparation des Couches

**Backend - Architecture Hexagonale (Clean Architecture)**

- **Routes/Controllers** : Point d'entrée HTTP uniquement, délègue immédiatement aux services
- **Services** : Logique métier, orchestration, AUCUN accès direct à la DB
- **Repositories** : Accès données exclusivement, requêtes SQL/ORM

Règles :

- Une route NE DOIT JAMAIS contenir de logique métier
- Un service NE DOIT JAMAIS importer SQLAlchemy directement
- Les dépendances pointent vers l'intérieur (Domain ne dépend de rien)

**Frontend - Organisation par feature**

- Composants Server Components par défaut
- Séparation claire : `components/`, `lib/`, `hooks/`, `actions/`
- API endpoints versionnés : `/api/v1/`

**API RESTful**

- Endpoints en kebab-case : `/api/v1/user-profiles`
- Verbes HTTP respectés : GET (lecture), POST (création), PUT/PATCH (modification), DELETE (suppression)
- Codes HTTP appropriés : 200/201/204 succès, 400 validation, 401 auth, 403 permissions, 404 not found, 500 erreur serveur

**Rationale** : Cette séparation permet de tester chaque couche indépendamment et facilite les changements futurs.

### III. Qualité & Tests (NON-NÉGOCIABLE)

**Couverture minimale OBLIGATOIRE**

- Backend : 80% de couverture de code
- Frontend : 70% de couverture de code

**Types de tests requis**

- **Tests unitaires** : pytest (backend), Jest ou Vitest (frontend)
- **Tests d'intégration** : Obligatoires pour tous les endpoints critiques (auth, paiements, données utilisateur)
- **Tests de contrat** : Pour les interfaces entre services

**Outils de qualité**

- Ruff pour le linting Python (remplace flake8, isort, black)
- ESLint + Prettier pour TypeScript/JavaScript
- Pre-commit hooks OBLIGATOIRES - aucun commit ne passe sans validation

**Cycle TDD encouragé**

1. Écrire le test (red)
2. Implémenter le minimum pour passer (green)
3. Refactoriser (refactor)

**Rationale** : Les tests sont la documentation exécutable du système et préviennent les régressions.

### IV. Sécurité (NON-NÉGOCIABLE)

**Authentification & Autorisation**

- JWT avec refresh tokens pour les sessions
- OAuth2 supporté : Google, GitHub
- Tokens stockés de manière sécurisée (httpOnly cookies, jamais localStorage pour les tokens sensibles)

**Validation des données**

- Validation côté CLIENT (UX) ET côté SERVEUR (sécurité)
- Jamais faire confiance aux données du client
- Pydantic côté backend, Zod recommandé côté frontend

**Protections obligatoires**

- Protection CSRF active sur tous les formulaires
- Rate limiting sur tous les endpoints publics
- Headers de sécurité : CSP, X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security
- CORS configuré strictement (jamais `*` en production)

**Gestion des secrets**

- JAMAIS de secrets en dur dans le code
- Variables d'environnement exclusivement
- Fichiers `.env` dans `.gitignore`
- Dependabot activé pour l'audit de dépendances

**Rationale** : La sécurité n'est pas une feature, c'est un prérequis. Une faille peut détruire la confiance des utilisateurs.

### V. Performance

**Temps de réponse API**

- 95% des requêtes DOIVENT répondre en < 200ms
- Alerting si p95 > 500ms

**Core Web Vitals (Frontend)**

- LCP (Largest Contentful Paint) : < 2.5s
- FID (First Input Delay) : < 100ms
- CLS (Cumulative Layout Shift) : < 0.1

**Stratégies de cache**

- Redis pour les données fréquemment accédées
- Cache HTTP approprié (Cache-Control headers)
- React Query / SWR pour le cache côté client

**Optimisation frontend**

- Lazy loading des composants non-critiques
- Code splitting automatique via Next.js
- Images optimisées via `next/image`
- Bundle analyzer exécuté avant chaque release majeure

**Rationale** : La performance impacte directement le SEO, la conversion, et la satisfaction utilisateur.

### VI. Expérience Développeur

**Documentation**

- README.md COMPLET avec : description, prérequis, instructions d'installation, commandes disponibles
- Instructions de setup en moins de 5 minutes
- Documentation API auto-générée (Swagger/OpenAPI)

**Environnement de développement**

- Docker Compose pour l'environnement local complet
- Hot reload actif en développement (frontend ET backend)
- Scripts npm/make pour les commandes courantes

**Logging & Observabilité**

- Logs structurés en JSON
- Corrélation des requêtes via request-id
- Niveaux de log appropriés : DEBUG, INFO, WARNING, ERROR, CRITICAL

**Rationale** : Un bon DX réduit le temps d'onboarding et augmente la productivité de l'équipe.

### VII. Conventions & Standards

**Commits conventionnels (OBLIGATOIRE)**

- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage (pas de changement de code)
- `refactor:` restructuration sans changement de comportement
- `test:` ajout/modification de tests
- `chore:` maintenance (dépendances, config)

**Branches**

- `main` : production, protégée
- `develop` : intégration
- `feature/xxx` : nouvelles fonctionnalités
- `bugfix/xxx` : corrections
- `hotfix/xxx` : corrections urgentes en production

**Nommage**

- Variables d'environnement : `SCREAMING_SNAKE_CASE`
- API endpoints : `kebab-case`, versionnés (`/api/v1/`)
- Fichiers Python : `snake_case.py`
- Fichiers TypeScript/Components : `PascalCase.tsx` (composants), `camelCase.ts` (utilitaires)

**Rationale** : Les conventions uniformes réduisent la charge cognitive et facilitent la collaboration.

## Stack Technique

| Couche          | Technologies                                                        |
| --------------- | ------------------------------------------------------------------- |
| Frontend        | Next.js 16+, TypeScript strict, TailwindCSS, Shadcn UI, Better Auth |
| Backend         | FastAPI, Python 3.12+, Pydantic, async/await                        |
| Base de données | PostgreSQL, SQLAlchemy, Alembic                                     |
| Cache           | Redis                                                               |
| Auth            | JWT, OAuth2 (Google, GitHub), Better Auth                           |
| Tests           | pytest, Jest/Vitest                                                 |
| CI/CD           | GitHub Actions, Docker, Vercel                                      |
| Qualité         | Ruff, ESLint, Prettier, pre-commit                                  |

## Workflow de Développement

**1. Création de feature**

1. Créer une branche `feature/xxx` depuis `develop`
2. Développer avec tests (TDD encouragé)
3. Pre-commit hooks passent automatiquement
4. Pull Request vers `develop`

**2. Code Review (obligatoire)**

- Au moins 1 approbation requise
- CI doit passer (tests, lint, build)
- Vérification de conformité à la constitution

**3. Déploiement**

- `develop` → staging automatique
- `main` → production après approbation
- Rollback automatisé disponible

**4. Hotfix**

- Branche `hotfix/xxx` depuis `main`
- Merge dans `main` ET `develop`
- Déploiement immédiat

## Governance

Cette constitution est le document de référence qui PRIME sur toutes les autres pratiques du projet.

**Conformité**

- Toute Pull Request DOIT être vérifiée pour conformité aux principes
- Les violations DOIVENT être justifiées et documentées
- L'équipe PEUT proposer des amendements via PR sur ce document

**Amendements**

- Tout changement de constitution nécessite :
  1. Une PR dédiée avec justification
  2. Revue par au moins 2 membres de l'équipe
  3. Plan de migration si breaking change
  4. Mise à jour de la version

**Versioning de la Constitution**

- MAJOR : Suppression/redéfinition de principes (breaking)
- MINOR : Ajout de principes ou expansion significative
- PATCH : Clarifications, corrections de typos

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
