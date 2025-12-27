/**
 * Example Component: Query Usage
 * Demonstrates how to use TanStack Query hooks in a component
 */

"use client";

import { Button } from "@/components/ui/button";
import { useCreateMutation, useCurrentUser, useDepartments } from "@/hooks/useQuery";

interface Department {
  id: string;
  name: string;
}

export function QueryExample() {
  // Example 1: Fetching data with useQuery
  const { data: user, isLoading: userLoading, error: userError } = useCurrentUser();

  // Example 2: Fetching list data
  const { data: departments = [], isLoading: deptsLoading } = useDepartments();

  // Example 3: Creating data with useMutation
  const createDepartment = useCreateMutation<Department, { name: string }>(
    "/departments",
    undefined, // Will handle invalidation manually for this example
    {
      onSuccess: (data) => {
        console.log("Department created:", data);
      },
    }
  );

  const handleCreateDepartment = () => {
    createDepartment.mutate({ name: "New Department" });
  };

  if (userLoading || deptsLoading) {
    return <div>Loading...</div>;
  }

  if (userError) {
    return <div>Error: {userError.message}</div>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Current User</h2>
        <pre className="bg-muted rounded p-2 text-sm">{JSON.stringify(user, null, 2)}</pre>
      </div>

      <div>
        <h2 className="text-lg font-semibold">Departments ({departments.length})</h2>
        <ul className="list-disc pl-5">
          {(departments as Department[]).map((dept) => (
            <li key={dept.id}>{dept.name}</li>
          ))}
        </ul>
      </div>

      <Button onClick={handleCreateDepartment} disabled={createDepartment.isPending}>
        {createDepartment.isPending ? "Creating..." : "Create Department"}
      </Button>
    </div>
  );
}

/**
 * Example: Optimistic Updates
 * Shows how to implement optimistic UI updates
 */
export function OptimisticExample() {
  const { data: departments = [] } = useDepartments();

  // Note: Implementation intentionally left as comments for reference
  // See documentation for complete optimistic update pattern

  return (
    <div>
      <p>Departments: {departments.length}</p>
      {/* Implementation here */}
    </div>
  );
}
