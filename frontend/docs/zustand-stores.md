# Zustand Stores Configuration

## Overview

Zustand est configuré pour gérer le state client de l'application avec:

- ✅ State d'authentification persisté (localStorage)
- ✅ State UI avec préférences persistées (thème, sidebar)
- ✅ DevTools intégrés en développement
- ✅ Hooks type-safe réutilisables

## Stores Disponibles

### 1. Auth Store (`stores/auth.ts`)

Gère l'état d'authentification de l'utilisateur.

#### État

```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
```

#### Actions

| Action                         | Description                            |
| ------------------------------ | -------------------------------------- |
| `setUser(user)`                | Met à jour l'utilisateur               |
| `setTokens(access, refresh)`   | Met à jour les tokens                  |
| `clearTokens()`                | Supprime les tokens                    |
| `setLoading(boolean)`          | Change l'état de chargement            |
| `login(user, access, refresh)` | Connecte l'utilisateur                 |
| `logout()`                     | Déconnecte l'utilisateur               |
| `updateUser(userData)`         | Met à jour partiellement l'utilisateur |

#### Persistence

Les données suivantes sont persistées dans `localStorage` sous la clé `auth-storage`:

- `user`
- `accessToken`
- `refreshToken`
- `isAuthenticated`

#### Utilisation

```tsx
import { useAuthStore } from "@/stores";

function UserProfile() {
  const { user, isAuthenticated, logout } = useAuthStore();

  if (!isAuthenticated) {
    return <div>Non connecté</div>;
  }

  return (
    <div>
      <p>Bienvenue, {user?.firstName}!</p>
      <button onClick={logout}>Se déconnecter</button>
    </div>
  );
}
```

### 2. UI Store (`stores/ui.ts`)

Gère l'état de l'interface utilisateur.

#### État

```typescript
interface UIState {
  // Sidebar
  isSidebarOpen: boolean;
  isSidebarCollapsed: boolean;

  // Modals
  activeModal: string | null;
  modalData: unknown;

  // Notifications
  notificationCount: number;

  // Theme
  theme: "light" | "dark" | "system";

  // Loading
  globalLoading: boolean;
}
```

#### Actions

| Action                         | Description                              |
| ------------------------------ | ---------------------------------------- |
| `toggleSidebar()`              | Toggle l'ouverture de la sidebar         |
| `setSidebarOpen(boolean)`      | Définit si la sidebar est ouverte        |
| `toggleSidebarCollapse()`      | Toggle l'état réduit de la sidebar       |
| `setSidebarCollapsed(boolean)` | Définit si la sidebar est réduite        |
| `openModal(id, data?)`         | Ouvre un modal avec données optionnelles |
| `closeModal()`                 | Ferme le modal actif                     |
| `setNotificationCount(n)`      | Définit le nombre de notifications       |
| `incrementNotificationCount()` | Incrémente les notifications             |
| `decrementNotificationCount()` | Décrémente les notifications             |
| `setTheme(theme)`              | Change le thème                          |
| `setGlobalLoading(boolean)`    | Définit le chargement global             |

#### Persistence

Les données suivantes sont persistées dans `localStorage` sous la clé `ui-storage`:

- `theme`
- `isSidebarCollapsed`

#### Utilisation

```tsx
import { useUIStore } from "@/stores";

function Sidebar() {
  const { isSidebarOpen, isSidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <aside className={cn("sidebar", !isSidebarOpen && "hidden", isSidebarCollapsed && "w-16")}>
      <button onClick={toggleSidebar}>Toggle</button>
    </aside>
  );
}
```

## Hook useAuth

Le hook `useAuth` encapsule la logique d'authentification avec l'API.

```tsx
import { useAuth } from "@/hooks/useAuth";

function LoginForm() {
  const { login, isLoading } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await login({ email, password });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" value={email} onChange={...} />
      <input type="password" value={password} onChange={...} />
      <button type="submit" disabled={isLoading}>
        {isLoading ? "Connexion..." : "Se connecter"}
      </button>
    </form>
  );
}
```

### Fonctions disponibles

| Fonction                         | Description                         |
| -------------------------------- | ----------------------------------- |
| `login(credentials)`             | Connecte avec email/password        |
| `register(data)`                 | Inscrit un nouvel utilisateur       |
| `logout()`                       | Déconnecte l'utilisateur            |
| `refreshToken()`                 | Rafraîchit le token d'accès         |
| `forgotPassword(email)`          | Envoie un email de réinitialisation |
| `resetPassword(token, password)` | Réinitialise le mot de passe        |

## Patterns et Best Practices

### 1. Accès en dehors des composants

```typescript
import { useAuthStore } from "@/stores";

// Accéder au state directement
const token = useAuthStore.getState().accessToken;

// S'abonner aux changements
const unsubscribe = useAuthStore.subscribe((state) => console.log("State changed:", state));
```

### 2. Sélecteurs pour optimiser les re-renders

```tsx
// ❌ Éviter - déclenche un re-render pour tout changement
const state = useAuthStore();

// ✅ Préférer - ne re-render que si user change
const user = useAuthStore((state) => state.user);
```

### 3. Combinaison de stores

```tsx
function Header() {
  const user = useAuthStore((state) => state.user);
  const notificationCount = useUIStore((state) => state.notificationCount);

  return (
    <header>
      <span>{user?.firstName}</span>
      <NotificationBell count={notificationCount} />
    </header>
  );
}
```

### 4. Gestion des modals

```tsx
import { useUIStore } from "@/stores";

// Ouvrir un modal avec des données
function openEditModal(userId: string) {
  useUIStore.getState().openModal("edit-user", { userId });
}

// Dans le composant modal
function EditUserModal() {
  const { activeModal, modalData, closeModal } = useUIStore();

  if (activeModal !== "edit-user") return null;

  return (
    <Dialog open onOpenChange={closeModal}>
      <DialogContent>
        <p>Editing user: {(modalData as { userId: string })?.userId}</p>
      </DialogContent>
    </Dialog>
  );
}
```

## DevTools

Les DevTools Zustand sont automatiquement activés en développement:

1. Ouvrir les DevTools du navigateur
2. Aller dans l'onglet "Redux DevTools" (nécessite l'extension)
3. Sélectionner "AuthStore" ou "UIStore" dans le dropdown

## Structure des fichiers

```
stores/
├── index.ts        # Barrel exports
├── auth.ts         # Auth store avec persistence
└── ui.ts           # UI store avec persistence thème
```

## Testing

Pour tester les composants utilisant les stores:

```tsx
import { act, renderHook } from "@testing-library/react";
import { useAuthStore } from "@/stores";

describe("AuthStore", () => {
  beforeEach(() => {
    // Reset store between tests
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it("should login user", () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.login(
        { id: "1", email: "test@example.com", ... },
        "access-token",
        "refresh-token"
      );
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user?.email).toBe("test@example.com");
  });
});
```

## Acceptance Criteria ✅

- [x] Zustand configuré
- [x] Auth store fonctionnel avec persistence
- [x] UI store avec thème et sidebar
- [x] Hooks de store utilisables partout
- [x] Persistence (localStorage) pour auth et UI preferences
- [x] DevTools en développement
- [x] Types TypeScript complets
