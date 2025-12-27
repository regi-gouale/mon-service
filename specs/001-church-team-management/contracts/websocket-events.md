# WebSocket Events Specification

## Overview

Ce document définit les événements WebSocket pour la communication temps réel dans l'application Church Team Management.

**Technologie**: Socket.IO avec Redis Adapter  
**Namespace**: `/ws`  
**URL Production**: `wss://api.monservice.com/ws`  
**URL Development**: `ws://localhost:8000/ws`

---

## Authentification

### Connexion

Le client doit envoyer le JWT dans le handshake:

```typescript
const socket = io("wss://api.monservice.com/ws", {
  auth: {
    token: "Bearer <access_token>",
  },
  transports: ["websocket", "polling"],
});
```

### Événements d'authentification

| Event          | Direction       | Payload                             | Description                       |
| -------------- | --------------- | ----------------------------------- | --------------------------------- |
| `auth:error`   | Server → Client | `{ code: string, message: string }` | Erreur d'authentification         |
| `auth:expired` | Server → Client | `{}`                                | Token expiré, rafraîchir le token |

---

## Rooms (Canaux)

### Structure des rooms

```
user:{user_id}           # Notifications personnelles
org:{organization_id}    # Événements organisation
dept:{department_id}     # Événements département
planning:{planning_id}   # Édition collaborative planning
```

### Rejoindre/Quitter les rooms

| Event         | Direction       | Payload                                 |
| ------------- | --------------- | --------------------------------------- |
| `room:join`   | Client → Server | `{ room: string }`                      |
| `room:leave`  | Client → Server | `{ room: string }`                      |
| `room:joined` | Server → Client | `{ room: string, users_count: number }` |
| `room:left`   | Server → Client | `{ room: string }`                      |

---

## Planning Events

### Édition collaborative en temps réel

| Event                           | Direction       | Payload                                             | Description           |
| ------------------------------- | --------------- | --------------------------------------------------- | --------------------- |
| `planning:assignment:created`   | Server → Client | `PlanningAssignmentEvent`                           | Nouvelle affectation  |
| `planning:assignment:updated`   | Server → Client | `PlanningAssignmentEvent`                           | Affectation modifiée  |
| `planning:assignment:deleted`   | Server → Client | `{ assignment_id: string }`                         | Affectation supprimée |
| `planning:published`            | Server → Client | `{ planning_id: string, published_at: string }`     | Planning publié       |
| `planning:generation:started`   | Server → Client | `{ planning_id: string, task_id: string }`          | Génération démarrée   |
| `planning:generation:progress`  | Server → Client | `PlanningGenerationProgress`                        | Progression           |
| `planning:generation:completed` | Server → Client | `{ planning_id: string, confidence_score: number }` | Génération terminée   |
| `planning:generation:failed`    | Server → Client | `{ planning_id: string, error: string }`            | Échec génération      |

#### PlanningAssignmentEvent

```typescript
interface PlanningAssignmentEvent {
  planning_id: string;
  assignment_id: string;
  service_id: string;
  member_id: string;
  assigned_role: string;
  status: "assigned" | "confirmed" | "declined" | "replaced";
  updated_by: {
    id: string;
    name: string;
  };
  timestamp: string; // ISO 8601
}
```

#### PlanningGenerationProgress

```typescript
interface PlanningGenerationProgress {
  planning_id: string;
  task_id: string;
  stage: "analyzing" | "assigning" | "optimizing" | "finalizing";
  progress: number; // 0-100
  services_processed: number;
  services_total: number;
  message?: string;
}
```

---

## Availability Events

| Event                            | Direction       | Payload                                                          | Description              |
| -------------------------------- | --------------- | ---------------------------------------------------------------- | ------------------------ |
| `availability:updated`           | Server → Client | `AvailabilityUpdateEvent`                                        | Indisponibilité modifiée |
| `availability:deadline:reminder` | Server → Client | `{ department_id: string, deadline: string, days_left: number }` | Rappel deadline          |

#### AvailabilityUpdateEvent

```typescript
interface AvailabilityUpdateEvent {
  department_id: string;
  member_id: string;
  month: string; // YYYY-MM
  dates_added: string[]; // ISO date strings
  dates_removed: string[]; // ISO date strings
  updated_at: string;
}
```

---

## Notification Events

| Event                | Direction       | Payload                       | Description           |
| -------------------- | --------------- | ----------------------------- | --------------------- |
| `notification:new`   | Server → Client | `NotificationEvent`           | Nouvelle notification |
| `notification:read`  | Server → Client | `{ notification_id: string }` | Notification lue      |
| `notification:count` | Server → Client | `{ unread_count: number }`    | Mise à jour compteur  |

#### NotificationEvent

```typescript
interface NotificationEvent {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  data: Record<string, unknown>;
  created_at: string;
}

type NotificationType =
  | "planning_published"
  | "assignment_created"
  | "assignment_reminder"
  | "availability_deadline"
  | "invitation_received"
  | "member_joined"
  | "service_report_created"
  | "shopping_item_assigned"
  | "dress_code_updated"
  | "event_reminder";
```

---

## Member Events

| Event            | Direction       | Payload                                        | Description           |
| ---------------- | --------------- | ---------------------------------------------- | --------------------- |
| `member:joined`  | Server → Client | `MemberJoinedEvent`                            | Nouveau membre        |
| `member:left`    | Server → Client | `{ department_id: string, member_id: string }` | Membre parti          |
| `member:updated` | Server → Client | `MemberUpdatedEvent`                           | Profil membre modifié |
| `member:online`  | Server → Client | `{ department_id: string, member_id: string }` | Membre en ligne       |
| `member:offline` | Server → Client | `{ department_id: string, member_id: string }` | Membre hors ligne     |

#### MemberJoinedEvent

```typescript
interface MemberJoinedEvent {
  department_id: string;
  member: {
    id: string;
    user: {
      id: string;
      first_name: string;
      last_name: string;
      avatar_url?: string;
    };
    role: "admin" | "manager" | "member";
    joined_at: string;
  };
}
```

---

## Shopping List Events (P4)

| Event                     | Direction       | Payload                                                      | Description     |
| ------------------------- | --------------- | ------------------------------------------------------------ | --------------- |
| `shopping:item:added`     | Server → Client | `ShoppingItemEvent`                                          | Article ajouté  |
| `shopping:item:purchased` | Server → Client | `{ list_id: string, item_id: string, purchased_by: string }` | Article acheté  |
| `shopping:list:completed` | Server → Client | `{ list_id: string }`                                        | Liste complétée |

---

## Presence (Curseurs collaboratifs)

Pour l'édition collaborative du planning:

| Event              | Direction       | Payload            | Description                  |
| ------------------ | --------------- | ------------------ | ---------------------------- |
| `presence:cursor`  | Client → Server | `CursorPosition`   | Position curseur             |
| `presence:cursors` | Server → Client | `CursorPosition[]` | Curseurs autres utilisateurs |

#### CursorPosition

```typescript
interface CursorPosition {
  user_id: string;
  user_name: string;
  avatar_url?: string;
  planning_id: string;
  service_id?: string;
  timestamp: number;
}
```

---

## Error Events

| Event              | Direction       | Payload       | Description       |
| ------------------ | --------------- | ------------- | ----------------- |
| `error`            | Server → Client | `SocketError` | Erreur générique  |
| `reconnect_failed` | Server → Client | `{}`          | Échec reconnexion |

#### SocketError

```typescript
interface SocketError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  correlation_id?: string;
}
```

### Codes d'erreur

| Code                 | Description              |
| -------------------- | ------------------------ |
| `AUTH_REQUIRED`      | Authentification requise |
| `AUTH_INVALID`       | Token invalide           |
| `AUTH_EXPIRED`       | Token expiré             |
| `ROOM_ACCESS_DENIED` | Accès au room refusé     |
| `RATE_LIMITED`       | Trop de messages         |
| `INVALID_PAYLOAD`    | Payload invalide         |

---

## Rate Limiting

- **Messages par connexion**: 100/minute
- **Événements presence**: 10/seconde max
- **Reconnexion**: Backoff exponentiel (1s, 2s, 4s, 8s, max 30s)

---

## Client Implementation Example

```typescript
// services/socket.ts
import { io, Socket } from "socket.io-client";
import { useAuthStore } from "@/stores/auth";

class SocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect() {
    const { accessToken } = useAuthStore.getState();

    this.socket = io(process.env.NEXT_PUBLIC_WS_URL!, {
      auth: { token: `Bearer ${accessToken}` },
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 30000,
    });

    this.setupListeners();
  }

  private setupListeners() {
    this.socket?.on("connect", () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
    });

    this.socket?.on("auth:expired", () => {
      // Rafraîchir le token et reconnecter
      this.handleTokenRefresh();
    });

    this.socket?.on("disconnect", (reason) => {
      if (reason === "io server disconnect") {
        // Reconnexion manuelle nécessaire
        this.connect();
      }
    });
  }

  joinDepartment(departmentId: string) {
    this.socket?.emit("room:join", { room: `dept:${departmentId}` });
  }

  leaveDepartment(departmentId: string) {
    this.socket?.emit("room:leave", { room: `dept:${departmentId}` });
  }

  onPlanningAssignment(callback: (event: PlanningAssignmentEvent) => void) {
    this.socket?.on("planning:assignment:created", callback);
    this.socket?.on("planning:assignment:updated", callback);
    return () => {
      this.socket?.off("planning:assignment:created", callback);
      this.socket?.off("planning:assignment:updated", callback);
    };
  }

  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
  }
}

export const socketService = new SocketService();
```

---

## Server Implementation Notes

### Redis Adapter Configuration

```python
# backend/app/core/websocket.py
import socketio
from app.core.config import settings

mgr = socketio.AsyncRedisManager(settings.REDIS_URL)
sio = socketio.AsyncServer(
    async_mode='asgi',
    client_manager=mgr,
    cors_allowed_origins=settings.CORS_ORIGINS,
    logger=True,
)
```

### Room Authorization Middleware

```python
@sio.event
async def room_join(sid, data):
    room = data.get('room')
    user = await get_user_from_session(sid)

    # Vérifier les permissions
    if room.startswith('dept:'):
        dept_id = room.split(':')[1]
        if not await user_has_department_access(user.id, dept_id):
            await sio.emit('error', {
                'code': 'ROOM_ACCESS_DENIED',
                'message': 'Access denied to this department'
            }, to=sid)
            return

    await sio.enter_room(sid, room)
    await sio.emit('room:joined', {'room': room}, to=sid)
```
