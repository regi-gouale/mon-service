# Research: Church Team Management SaaS

**Feature**: 001-church-team-management
**Date**: 2025-12-27
**Purpose**: Résoudre toutes les questions techniques et documenter les décisions d'architecture

## 1. Algorithme de Génération de Planning

### Question

Comment implémenter un algorithme de génération de planning qui respecte les contraintes d'indisponibilité, assure l'équité de rotation, et s'exécute en moins de 10 secondes ?

### Décision

Utiliser un algorithme glouton (greedy) avec scoring pondéré, exécuté en tâche Celery asynchrone.

### Rationale

- Un algorithme glouton est suffisant pour la taille du problème (< 100 membres, < 50 services/mois)
- Complexité O(n × m) où n = services, m = membres disponibles
- Les algorithmes d'optimisation (génétique, recuit simulé) seraient surdimensionnés
- L'approche par scoring permet d'ajuster facilement les critères de priorité

### Alternatives Considérées

| Alternative                   | Rejetée car                                           |
| ----------------------------- | ----------------------------------------------------- |
| Programmation linéaire (PuLP) | Complexité excessive pour le problème, temps de setup |
| Algorithme génétique          | Temps d'exécution imprévisible, surdimensionné        |
| Affectation aléatoire         | Pas d'équité garantie                                 |

### Implémentation Détaillée

```python
# Pseudo-code de l'algorithme
def generate_planning(department_id: UUID, month: date) -> Planning:
    services = get_services_for_month(department_id, month)
    members = get_active_members(department_id)
    availabilities = get_availabilities(department_id, month)
    history = get_participation_history(department_id, months=3)

    assignments = []
    for service in services:
        available_members = filter_available(members, availabilities, service.date)
        scored_members = score_members(available_members, service, history)

        for role in service.required_roles:
            best_member = select_best_for_role(scored_members, role)
            if best_member:
                assignments.append(Assignment(member=best_member, service=service, role=role))
                update_history_cache(best_member)

    return Planning(assignments=assignments, confidence_score=calculate_confidence())
```

### Critères de Scoring

| Critère                     | Poids | Description                                                        |
| --------------------------- | ----- | ------------------------------------------------------------------ |
| Équité de rotation          | 40%   | Favoriser les membres avec moins de participations récentes        |
| Compétences correspondantes | 30%   | Bonus si le membre a le rôle requis                                |
| Préférences                 | 20%   | Bonus si le membre a marqué une préférence pour ce type de service |
| Repos minimum               | 10%   | Malus si service précédent trop proche                             |

---

## 2. Multi-Tenancy et Isolation des Données

### Question

Comment assurer une isolation stricte des données entre organisations tout en maintenant de bonnes performances ?

### Décision

Multi-tenancy par colonne `organization_id` sur toutes les tables avec middleware de validation obligatoire.

### Rationale

- Plus simple que le multi-tenancy par schéma ou par base de données
- Permet une gestion unifiée des migrations
- Performance acceptable avec index sur `organization_id`
- Row Level Security (RLS) PostgreSQL en option pour sécurité renforcée

### Alternatives Considérées

| Alternative                | Rejetée car                                                   |
| -------------------------- | ------------------------------------------------------------- |
| Base de données par tenant | Complexité de gestion, coûts élevés                           |
| Schéma par tenant          | Migrations complexes, pas adapté à un grand nombre de tenants |
| Filtrage applicatif seul   | Risque d'erreur, pas de garantie DB                           |

### Implémentation

```python
# Middleware FastAPI obligatoire
async def validate_organization_access(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> UUID:
    org_id = current_user.organization_id
    if not org_id:
        raise HTTPException(status_code=403, detail="No organization access")
    # Injecter dans toutes les requêtes
    request.state.organization_id = org_id
    return org_id

# Repository base avec filtre automatique
class BaseRepository:
    async def get_all(self, organization_id: UUID) -> list[Model]:
        query = select(self.model).where(
            self.model.organization_id == organization_id
        )
        return await self.session.execute(query)
```

---

## 3. Authentification et Gestion des Sessions

### Question

Comment gérer l'authentification de manière sécurisée entre frontend (Better Auth) et backend (FastAPI) ?

### Décision

Architecture hybride : Better Auth côté frontend pour OAuth/sessions, validation JWT côté backend.

### Rationale

- Better Auth simplifie l'intégration OAuth côté Next.js
- Le backend valide les tokens JWT de manière stateless
- Les refresh tokens permettent des sessions longues sans stocker d'état serveur

### Flux d'Authentification

```
1. Utilisateur → Frontend (Better Auth)
2. Frontend → Google OAuth → Callback → Session créée
3. Frontend récupère JWT access token
4. Frontend → Backend API avec Bearer token
5. Backend valide JWT, extrait user_id et organization_id
6. Refresh token automatique avant expiration
```

### Configuration JWT

| Paramètre                | Valeur          | Justification                                          |
| ------------------------ | --------------- | ------------------------------------------------------ |
| Access token expiration  | 15 minutes      | Sécurité, limite exposition si compromis               |
| Refresh token expiration | 7 jours         | UX, évite reconnexions fréquentes                      |
| Algorithme               | RS256           | Asymétrique, backend peut vérifier sans secret partagé |
| Stockage refresh         | httpOnly cookie | Protection XSS                                         |

---

## 4. WebSockets et Communication Temps Réel

### Question

Comment implémenter les notifications temps réel de manière scalable ?

### Décision

Socket.io avec adapter Redis pour scalabilité horizontale.

### Rationale

- Socket.io offre fallback automatique (long-polling si WebSocket indisponible)
- L'adapter Redis permet plusieurs instances backend
- Pattern room natif pour isolation par organisation/département

### Implémentation

```python
# Backend - python-socketio
import socketio

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['https://app.monservice.com'],
    client_manager=socketio.AsyncRedisManager('redis://redis:6379')
)

@sio.on('connect')
async def connect(sid, environ, auth):
    user = await validate_socket_auth(auth['token'])
    await sio.enter_room(sid, f"org:{user.organization_id}")
    await sio.enter_room(sid, f"dept:{user.department_id}")
    await sio.enter_room(sid, f"user:{user.id}")

# Émettre une notification
async def notify_planning_published(department_id: UUID, planning: Planning):
    await sio.emit('planning:published', planning.dict(), room=f"dept:{department_id}")
```

### Événements WebSocket

| Événement               | Room        | Payload              | Déclencheur            |
| ----------------------- | ----------- | -------------------- | ---------------------- |
| `planning:published`    | `dept:{id}` | Planning complet     | Publication planning   |
| `planning:updated`      | `dept:{id}` | Diff des changements | Modification planning  |
| `availability:changed`  | `dept:{id}` | Member + dates       | Saisie indisponibilité |
| `notification:new`      | `user:{id}` | Notification         | Toute notification     |
| `shopping-list:updated` | `dept:{id}` | Liste mise à jour    | Modification liste     |

---

## 5. Stockage de Fichiers (S3)

### Question

Comment organiser le stockage des images (dress codes, rapports, profils) ?

### Décision

Hetzner Object Storage avec structure de buckets par type et organisation.

### Rationale

- Hetzner Object Storage est S3-compatible et économique
- Structure par organisation permet isolation et nettoyage facile
- URLs pré-signées pour accès sécurisé temporaire

### Structure des Buckets

```
mon-service-uploads/
├── {organization_id}/
│   ├── dress-codes/
│   │   └── {dress_code_id}/{filename}
│   ├── reports/
│   │   └── {report_id}/{filename}
│   ├── profiles/
│   │   └── {user_id}/{filename}
│   └── inventory/
│       └── {item_id}/{filename}
```

### Configuration

```python
# Génération d'URL pré-signée pour upload
async def generate_upload_url(
    organization_id: UUID,
    category: str,
    entity_id: UUID,
    filename: str
) -> str:
    key = f"{organization_id}/{category}/{entity_id}/{filename}"
    return s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': BUCKET_NAME, 'Key': key},
        ExpiresIn=3600  # 1 heure
    )
```

---

## 6. Tâches Asynchrones (Celery)

### Question

Quelles tâches doivent être exécutées en arrière-plan ?

### Décision

Celery avec Redis comme broker pour les tâches longues ou différées.

### Tâches Identifiées

| Tâche                          | Priorité | Timeout | Retry |
| ------------------------------ | -------- | ------- | ----- |
| `generate_planning`            | high     | 30s     | 1     |
| `send_email`                   | medium   | 10s     | 3     |
| `send_push_notification`       | medium   | 5s      | 3     |
| `cleanup_expired_invitations`  | low      | 60s     | 0     |
| `generate_planning_export_pdf` | medium   | 30s     | 1     |

### Configuration Celery Beat (Scheduler)

```python
# Tâches périodiques
CELERYBEAT_SCHEDULE = {
    'send-service-reminders': {
        'task': 'workers.tasks.send_service_reminders',
        'schedule': crontab(hour=8, minute=0),  # Tous les jours à 8h
    },
    'cleanup-expired-invitations': {
        'task': 'workers.tasks.cleanup_expired_invitations',
        'schedule': crontab(hour=2, minute=0),  # Tous les jours à 2h
    },
    'send-availability-reminders': {
        'task': 'workers.tasks.send_availability_reminders',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Lundi 9h
    },
}
```

---

## 7. Internationalisation

### Question

Comment gérer l'internationalisation (français par défaut, anglais futur) ?

### Décision

next-intl côté frontend avec fichiers JSON par locale, backend renvoie des clés i18n.

### Rationale

- next-intl s'intègre nativement avec App Router
- Le backend reste agnostique de la langue (renvoie des clés)
- Permet d'ajouter des langues sans modifier le backend

### Structure

```
frontend/
├── messages/
│   ├── fr.json
│   └── en.json  # Futur
├── src/
│   ├── i18n.ts
│   └── middleware.ts  # Détection locale
```

---

## 8. Monitoring et Observabilité

### Question

Comment monitorer l'application en production ?

### Décision

Stack auto-hébergée : Prometheus + Grafana + Loki.

### Rationale

- Auto-hébergé = pas de coûts SaaS récurrents
- Prometheus natif avec FastAPI via `prometheus-fastapi-instrumentator`
- Grafana offre dashboards personnalisables
- Loki pour centralisation des logs

### Métriques Clés

| Métrique               | Seuil Alerte | Action                                |
| ---------------------- | ------------ | ------------------------------------- |
| API latency p95        | > 500ms      | Investiguer requêtes lentes           |
| Error rate             | > 1%         | Vérifier logs, rollback si nécessaire |
| Celery queue length    | > 100        | Ajouter workers                       |
| Redis memory           | > 80%        | Ajuster TTL cache                     |
| PostgreSQL connections | > 80% pool   | Augmenter pool size                   |

---

## 9. Sécurité RGPD

### Question

Comment assurer la conformité RGPD pour les données personnelles ?

### Décision

Implémentation des droits RGPD (accès, rectification, suppression) avec audit trail.

### Données Personnelles Identifiées

| Donnée                    | Catégorie | Rétention               | Chiffrement   |
| ------------------------- | --------- | ----------------------- | ------------- |
| Email                     | Identité  | Durée du compte + 3 ans | Transit (TLS) |
| Nom                       | Identité  | Durée du compte + 3 ans | Transit (TLS) |
| Photo profil              | Identité  | Durée du compte         | At-rest (S3)  |
| Indisponibilités          | Usage     | 12 mois glissants       | Non           |
| Historique participations | Usage     | 12 mois glissants       | Non           |

### Endpoints RGPD

- `GET /api/v1/users/me/data-export` - Export données personnelles (JSON)
- `DELETE /api/v1/users/me` - Suppression compte (anonymisation)
- `PUT /api/v1/users/me` - Rectification données

---

## 10. Gestion des Erreurs et Logs

### Question

Comment structurer la gestion des erreurs et les logs ?

### Décision

Exceptions personnalisées avec codes d'erreur, logs JSON avec correlation ID.

### Structure des Erreurs API

```python
class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

# Réponse standardisée
{
    "error": {
        "code": "PLANNING_CONFLICT",
        "message": "Member is not available on this date",
        "details": {
            "member_id": "...",
            "date": "2025-01-15"
        },
        "correlation_id": "abc-123-def"
    }
}
```

### Format des Logs

```json
{
  "timestamp": "2025-12-27T10:30:00Z",
  "level": "INFO",
  "correlation_id": "abc-123-def",
  "user_id": "user-uuid",
  "organization_id": "org-uuid",
  "message": "Planning generated successfully",
  "extra": {
    "department_id": "dept-uuid",
    "assignments_count": 45,
    "duration_ms": 2340
  }
}
```

---

## Résumé des Décisions

| Domaine             | Décision                                          | Confidence |
| ------------------- | ------------------------------------------------- | ---------- |
| Algorithme planning | Greedy avec scoring pondéré                       | Haute      |
| Multi-tenancy       | Colonne `organization_id` + middleware            | Haute      |
| Auth                | Better Auth (frontend) + JWT validation (backend) | Haute      |
| WebSockets          | Socket.io + Redis adapter                         | Haute      |
| Stockage fichiers   | Hetzner S3 + URLs pré-signées                     | Haute      |
| Tâches async        | Celery + Redis broker                             | Haute      |
| i18n                | next-intl                                         | Haute      |
| Monitoring          | Prometheus + Grafana + Loki                       | Haute      |
| RGPD                | Endpoints dédiés + audit trail                    | Haute      |
| Logs                | JSON structuré + correlation ID                   | Haute      |
