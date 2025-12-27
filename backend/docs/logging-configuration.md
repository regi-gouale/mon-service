# Structured JSON Logging Configuration

Ce document décrit la configuration de la journalisation JSON structurée avec correlation ID pour le backend FastAPI.

## Vue d'ensemble

Le système de logging fournit:

- **Logs JSON structurés** compatibles avec Loki, ELK Stack, Datadog, etc.
- **Correlation ID** unique par requête pour le traçage distribué
- **Métriques de performance** (durée, codes de statut)
- **Contexte asynchrone** pour la propagation du correlation ID

## Configuration

### Variables d'environnement

| Variable     | Valeur par défaut | Description                                           |
| ------------ | ----------------- | ----------------------------------------------------- |
| `LOG_LEVEL`  | `INFO`            | Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FORMAT` | `json`            | Format de sortie (`json` ou `text`)                   |

### Exemple `.env`

```bash
# Production - JSON pour log aggregation
LOG_LEVEL=INFO
LOG_FORMAT=json

# Développement - Texte lisible
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

## Format des logs JSON

Chaque ligne de log est un objet JSON valide:

```json
{
  "timestamp": "2025-12-27T10:30:00.000000+00:00",
  "level": "INFO",
  "logger": "app.core.middleware",
  "message": "Request completed",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "service": "church-team-management",
  "environment": "production",
  "event": "request_completed",
  "http_method": "GET",
  "http_path": "/api/v1/users",
  "http_status": 200,
  "duration_ms": 42.15
}
```

### Champs standards

| Champ            | Type     | Description                                      |
| ---------------- | -------- | ------------------------------------------------ |
| `timestamp`      | ISO 8601 | Horodatage UTC                                   |
| `level`          | string   | Niveau de log                                    |
| `logger`         | string   | Nom du logger                                    |
| `message`        | string   | Message de log                                   |
| `correlation_id` | UUID     | ID unique de la requête                          |
| `service`        | string   | Nom du service                                   |
| `environment`    | string   | Environnement (development, staging, production) |

### Champs additionnels pour les requêtes HTTP

| Champ         | Description                                                           |
| ------------- | --------------------------------------------------------------------- |
| `event`       | Type d'événement (request_started, request_completed, request_failed) |
| `http_method` | Méthode HTTP (GET, POST, etc.)                                        |
| `http_path`   | Chemin de la requête                                                  |
| `http_status` | Code de statut HTTP                                                   |
| `duration_ms` | Durée de la requête en millisecondes                                  |
| `client_ip`   | Adresse IP du client                                                  |
| `user_agent`  | User-Agent du client                                                  |

### Champs pour les erreurs

```json
{
  "level": "ERROR",
  "message": "Request failed",
  "exception": {
    "type": "ValueError",
    "message": "Invalid input",
    "traceback": "Traceback (most recent call last)..."
  },
  "location": {
    "file": "auth.py",
    "line": 42,
    "function": "validate_token"
  }
}
```

## Correlation ID

### Fonctionnement

1. **Génération**: Un UUID v4 est généré pour chaque requête
2. **Propagation**: Le header `X-Correlation-ID` est accepté en entrée
3. **Réponse**: Le correlation ID est ajouté aux headers de réponse
4. **Logs**: Tous les logs incluent automatiquement le correlation ID

### Headers HTTP

**Requête** (optionnel):

```http
GET /api/v1/users HTTP/1.1
X-Correlation-ID: custom-request-id-12345
```

**Réponse** (toujours présent):

```http
HTTP/1.1 200 OK
X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000
```

### Utilisation dans le code

```python
from app.core.logging import get_logger, correlation_id_context, get_correlation_id

logger = get_logger(__name__)

# Le correlation_id est automatiquement inclus dans tous les logs
logger.info("Processing user", extra={"user_id": 123})

# Accéder au correlation ID actuel
current_id = get_correlation_id()

# Créer un contexte avec un correlation ID spécifique (pour les workers)
with correlation_id_context("custom-id"):
    logger.info("This log will have correlation_id=custom-id")
```

## Intégration avec les systèmes de log aggregation

### Loki (Grafana)

Configuration Promtail:

```yaml
scrape_configs:
  - job_name: church-team-management
    static_configs:
      - targets:
          - localhost
        labels:
          job: church-team-management
          __path__: /var/log/app/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            correlation_id: correlation_id
            http_status: http_status
      - labels:
          level:
          correlation_id:
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

Configuration Filebeat:

```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/app/*.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "church-team-management-%{+yyyy.MM.dd}"
```

### Datadog

Configuration Docker:

```yaml
labels:
  com.datadoghq.ad.logs: '[{"source": "python", "service": "church-team-management"}]'
```

## Bonnes pratiques

### 1. Utiliser des champs structurés

```python
# ✅ Bon - Champs structurés
logger.info("User created", extra={
    "user_id": user.id,
    "email": user.email,
    "organization_id": user.organization_id,
})

# ❌ Mauvais - Interpolation de chaînes
logger.info(f"User {user.id} created with email {user.email}")
```

### 2. Niveaux de log appropriés

| Niveau   | Usage                                              |
| -------- | -------------------------------------------------- |
| DEBUG    | Informations de débogage détaillées                |
| INFO     | Événements normaux (requêtes, opérations réussies) |
| WARNING  | Situations anormales non critiques                 |
| ERROR    | Erreurs qui n'empêchent pas le fonctionnement      |
| CRITICAL | Erreurs fatales nécessitant une intervention       |

### 3. Éviter les informations sensibles

```python
# ✅ Bon
logger.info("Authentication attempt", extra={"email": user.email})

# ❌ Mauvais - Ne jamais logger de mots de passe
logger.info("Login", extra={"password": password})
```

## Tests

Exécuter les tests du module de logging:

```bash
cd backend
uv run pytest tests/unit/test_logging.py tests/unit/test_middleware.py -v
```

## Dépannage

### Les logs n'apparaissent pas en JSON

Vérifiez que `LOG_FORMAT=json` est défini dans les variables d'environnement.

### Le correlation ID n'apparaît pas

Assurez-vous que le middleware `CorrelationIdMiddleware` est ajouté à l'application FastAPI.

### Logs dupliqués

Le setup de logging utilise `root_logger.handlers.clear()` pour éviter les doublons. Si vous voyez des logs dupliqués, vérifiez qu'aucun autre code ne configure le logging.
