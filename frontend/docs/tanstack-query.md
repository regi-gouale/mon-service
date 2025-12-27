# TanStack Query Configuration

## Overview

TanStack Query (React Query v5) est configuré pour gérer le state serveur de l'application. Cette configuration fournit:

- ✅ Cache intelligent avec invalidation automatique
- ✅ Gestion des erreurs globale avec toasts
- ✅ Retry policy configurable
- ✅ Optimistic updates
- ✅ DevTools en développement
- ✅ Hooks personnalisés type-safe

## Configuration

### Query Client (`lib/query-client.ts`)

Configuration par défaut:

```typescript
{
  queries: {
    gcTime: 5 minutes,        // Cache time
    staleTime: 30 seconds,    // Data freshness
    retry: 1,                 // Retry once on failure
    refetchOnWindowFocus: production only,
  },
  mutations: {
    retry: 0,                 // No retry for mutations
  }
}
```

### Query Keys

Les clés sont centralisées dans `queryKeys` pour assurer la cohérence:

```typescript
import { queryKeys } from "@/lib/query-client";

// Auth
queryKeys.auth.me;

// Departments
queryKeys.departments.all;
queryKeys.departments.detail(id);
queryKeys.departments.members(id);

// Availabilities
queryKeys.availabilities.member(memberId, month);
queryKeys.availabilities.department(deptId, month);

// Plannings
queryKeys.plannings.all(deptId);
queryKeys.plannings.detail(id);

// Notifications
queryKeys.notifications.all;
queryKeys.notifications.unread;
```

## Usage

### 1. Fetching Data (useQuery)

```tsx
import { useCurrentUser, useDepartments } from "@/hooks/useQuery";

function MyComponent() {
  // Simple query
  const { data, isLoading, error } = useCurrentUser();

  // Query with options
  const { data: departments } = useDepartments({
    staleTime: 60000, // Override default stale time
    enabled: someCondition, // Conditional fetching
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>{data.name}</div>;
}
```

### 2. Creating Data (useMutation)

```tsx
import { useCreateMutation } from "@/hooks/useQuery";
import { queryKeys } from "@/lib/query-client";

function CreateDepartmentForm() {
  const createDepartment = useCreateMutation(
    "/departments",
    [queryKeys.departments.all], // Keys to invalidate on success
    {
      onSuccess: (data) => {
        toast.success("Department created!");
      },
    }
  );

  const handleSubmit = (formData) => {
    createDepartment.mutate(formData);
  };

  return (
    <button onClick={handleSubmit} disabled={createDepartment.isPending}>
      {createDepartment.isPending ? "Creating..." : "Create"}
    </button>
  );
}
```

### 3. Updating Data (useMutation)

```tsx
import { useUpdateMutation } from "@/hooks/useQuery";
import { queryKeys } from "@/lib/query-client";

function UpdateDepartment({ id }) {
  const updateDepartment = useUpdateMutation(
    (data) => `/departments/${data.id}`, // Dynamic endpoint
    [queryKeys.departments.all, queryKeys.departments.detail(id)]
  );

  return <button onClick={() => updateDepartment.mutate({ id, name: "Updated" })}>Update</button>;
}
```

### 4. Optimistic Updates

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-client";

function OptimisticToggle() {
  const queryClient = useQueryClient();

  const toggle = useMutation({
    mutationFn: (id) => api.patch(`/items/${id}/toggle`),
    onMutate: async (id) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.items.all });

      // Snapshot previous value
      const previous = queryClient.getQueryData(queryKeys.items.all);

      // Optimistically update
      queryClient.setQueryData(queryKeys.items.all, (old) =>
        old.map((item) => (item.id === id ? { ...item, completed: !item.completed } : item))
      );

      // Return context with snapshot
      return { previous };
    },
    onError: (err, id, context) => {
      // Rollback on error
      queryClient.setQueryData(queryKeys.items.all, context.previous);
    },
    onSettled: () => {
      // Refetch after error or success
      queryClient.invalidateQueries({ queryKey: queryKeys.items.all });
    },
  });

  return <button onClick={() => toggle.mutate(itemId)}>Toggle</button>;
}
```

### 5. Prefetching

```tsx
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-client";

function DepartmentList() {
  const queryClient = useQueryClient();

  const handleMouseEnter = (deptId) => {
    // Prefetch on hover
    queryClient.prefetchQuery({
      queryKey: queryKeys.departments.detail(deptId),
      queryFn: () => api.get(`/departments/${deptId}`),
    });
  };

  return <div onMouseEnter={() => handleMouseEnter(id)}>...</div>;
}
```

## Custom Hooks

Créez des hooks spécifiques pour votre domaine:

```typescript
// hooks/useDepartments.ts
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/query-client";

export function useDepartments() {
  return useQuery({
    queryKey: queryKeys.departments.all,
    queryFn: () => api.get("/departments"),
  });
}
```

## Error Handling

### Global Error Handling

Les erreurs sont gérées globalement dans `query-client.ts`:

- Queries en background affichent un toast
- Mutations affichent toujours un toast d'erreur

### Local Error Handling

```tsx
const { error, isError } = useQuery({
  queryKey: ["user"],
  queryFn: fetchUser,
  retry: false, // Disable retry for this query
});

if (isError) {
  return <div>Error: {error.message}</div>;
}
```

## DevTools

Les DevTools sont automatiquement inclus en développement:

- Accessible en bas de l'écran
- Permet d'inspecter les queries et mutations
- Affiche le cache et les invalidations

## Best Practices

1. **Toujours utiliser les query keys centralisées** (`queryKeys`)
2. **Invalider les queries après mutations** pour garder les données à jour
3. **Utiliser `enabled`** pour les queries conditionnelles
4. **Préférer les hooks personnalisés** pour réutilisabilité
5. **Gérer les états de chargement** (isLoading, isPending)
6. **Implémenter des optimistic updates** pour une meilleure UX
7. **Utiliser prefetching** pour améliorer les performances

## Troubleshooting

### Query ne se refetch pas

Vérifiez:

- `staleTime` est peut-être trop long
- `enabled` est peut-être false
- La query key change-t-elle correctement?

### Mutation ne met pas à jour l'UI

Assurez-vous d'invalider les bonnes queries:

```typescript
const mutation = useMutation({
  mutationFn: updateData,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["data"] });
  },
});
```

### Trop de requêtes

- Augmentez `staleTime`
- Désactivez `refetchOnWindowFocus`
- Utilisez `enabled: false` pour les queries conditionnelles

## References

- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [Query Keys Best Practices](https://tanstack.com/query/latest/docs/react/guides/query-keys)
- [Optimistic Updates Guide](https://tanstack.com/query/latest/docs/react/guides/optimistic-updates)
