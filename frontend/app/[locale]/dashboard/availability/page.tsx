/**
 * Availability Page
 *
 * Page for members to mark their unavailable dates for a specific month.
 * Includes month navigation, save functionality, and deadline awareness.
 */

"use client";

import { AvailabilityCalendar } from "@/components/calendar/availability-calendar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  useAvailabilityDeadline,
  useDepartments,
  useMyAvailabilities,
  useUpdateMyAvailabilities,
} from "@/hooks/useQuery";
import {
  getMockAvailabilityDeadline,
  getMockMyAvailabilities,
  mockDepartments,
  simulateDelay,
  type MockDepartment,
} from "@/lib/mock-data";
import type { AvailabilityDeadlineResponse, Department, MemberAvailabilityResponse } from "@/types";
import { IconDeviceFloppy, IconLoader2 } from "@tabler/icons-react";
import { useTranslations } from "next-intl";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

// ============================================================================
// Types
// ============================================================================

interface MonthYear {
  year: number;
  month: number;
}

// ============================================================================
// Helpers
// ============================================================================

function formatDeadlineDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function getCurrentMonthYear(): MonthYear {
  const now = new Date();
  return {
    year: now.getFullYear(),
    month: now.getMonth() + 1, // 1-indexed
  };
}

function getPreviousMonth(current: MonthYear): MonthYear {
  if (current.month === 1) {
    return { year: current.year - 1, month: 12 };
  }
  return { year: current.year, month: current.month - 1 };
}

function getNextMonth(current: MonthYear): MonthYear {
  if (current.month === 12) {
    return { year: current.year + 1, month: 1 };
  }
  return { year: current.year, month: current.month + 1 };
}

// ============================================================================
// Component
// ============================================================================

// Check if we're in mock mode
const isMockMode = process.env.NEXT_PUBLIC_MOCK_API === "true";

export default function AvailabilityPage() {
  const t = useTranslations("Availability");
  const tCommon = useTranslations("Common");

  // Mock mode state
  const [mockLoading, setMockLoading] = useState(isMockMode);
  const [mockSaving, setMockSaving] = useState(false);

  // Initialize mock loading
  useEffect(() => {
    if (isMockMode) {
      simulateDelay(500).then(() => setMockLoading(false));
    }
  }, []);

  // Fetch departments list (real API)
  const {
    data: departmentsData,
    isLoading: isLoadingDepartmentsApi,
    isError: isDepartmentsErrorApi,
  } = useDepartments({ enabled: !isMockMode });

  // Use mock or real data
  const isLoadingDepartments = isMockMode ? mockLoading : isLoadingDepartmentsApi;
  const isDepartmentsError = isMockMode ? false : isDepartmentsErrorApi;

  // Type-safe departments accessor with useMemo to prevent re-renders
  const departments = useMemo(() => {
    if (isMockMode) {
      return mockDepartments as unknown as (Department | MockDepartment)[];
    }
    return (departmentsData as Department[] | undefined) ?? [];
  }, [departmentsData]);

  // Selected department
  const [selectedDepartmentId, setSelectedDepartmentId] = useState<string | null>(null);

  // Auto-select first department when loaded
  useEffect(() => {
    if (departments.length > 0 && !selectedDepartmentId) {
      setSelectedDepartmentId(departments[0].id);
    }
  }, [departments, selectedDepartmentId]);

  // Current displayed month
  const [currentMonth, setCurrentMonth] = useState<MonthYear>(getCurrentMonthYear);

  // Selected unavailable dates
  const [selectedDates, setSelectedDates] = useState<Set<string>>(new Set());

  // Track if there are unsaved changes
  const [hasChanges, setHasChanges] = useState(false);

  // Fetch current availabilities (only when department is selected) - real API
  const {
    data: availabilityDataApi,
    isLoading: isLoadingAvailabilitiesApi,
    isError: isAvailabilityErrorApi,
  } = useMyAvailabilities(selectedDepartmentId ?? "", currentMonth.year, currentMonth.month, {
    enabled: !!selectedDepartmentId && !isMockMode,
  });

  // Fetch deadline info (only when department is selected) - real API
  const { data: deadlineDataApi, isLoading: isLoadingDeadlineApi } = useAvailabilityDeadline(
    selectedDepartmentId ?? "",
    currentMonth.year,
    currentMonth.month,
    { enabled: !!selectedDepartmentId && !isMockMode }
  );

  // Mutation for saving availabilities
  const updateMutation = useUpdateMyAvailabilities(selectedDepartmentId ?? "");

  // Get mock data when in mock mode
  const mockAvailabilityData = useMemo(() => {
    if (isMockMode && selectedDepartmentId) {
      return getMockMyAvailabilities(selectedDepartmentId, currentMonth.year, currentMonth.month);
    }
    return null;
  }, [selectedDepartmentId, currentMonth.year, currentMonth.month]);

  const mockDeadlineData = useMemo(() => {
    if (isMockMode) {
      return getMockAvailabilityDeadline(currentMonth.year, currentMonth.month);
    }
    return null;
  }, [currentMonth.year, currentMonth.month]);

  // Use mock or real data
  const isLoadingAvailabilities = isMockMode ? mockLoading : isLoadingAvailabilitiesApi;
  const isLoadingDeadline = isMockMode ? mockLoading : isLoadingDeadlineApi;
  const isAvailabilityError = isMockMode ? false : isAvailabilityErrorApi;

  // Type-safe accessors
  const typedAvailabilityData = isMockMode
    ? (mockAvailabilityData as unknown as MemberAvailabilityResponse)
    : (availabilityDataApi as MemberAvailabilityResponse | undefined);
  const typedDeadlineData = isMockMode
    ? (mockDeadlineData as unknown as AvailabilityDeadlineResponse)
    : (deadlineDataApi as AvailabilityDeadlineResponse | undefined);

  // Initialize selected dates from fetched data
  useEffect(() => {
    if (typedAvailabilityData?.unavailableDates) {
      const dates = new Set(typedAvailabilityData.unavailableDates.map((d) => d.date));
      setSelectedDates(dates);
      setHasChanges(false);
    }
  }, [typedAvailabilityData]);

  // Reset selected dates when department changes
  useEffect(() => {
    setSelectedDates(new Set());
    setHasChanges(false);
  }, [selectedDepartmentId]);

  // Handle date selection changes
  const handleDatesChange = useCallback((newDates: Set<string>) => {
    setSelectedDates(newDates);
    setHasChanges(true);
  }, []);

  // Handle month navigation
  const handlePreviousMonth = useCallback(() => {
    setCurrentMonth((prev) => getPreviousMonth(prev));
    setHasChanges(false);
  }, []);

  const handleNextMonth = useCallback(() => {
    setCurrentMonth((prev) => getNextMonth(prev));
    setHasChanges(false);
  }, []);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!selectedDepartmentId) return;

    // Convert selected dates to the request format
    const unavailableDates = Array.from(selectedDates)
      .filter((dateStr) => {
        const [y, m] = dateStr.split("-").map(Number);
        return y === currentMonth.year && m === currentMonth.month;
      })
      .map((date) => ({
        date,
        isAllDay: true,
        reason: undefined,
      }));

    // Mock mode: simulate save
    if (isMockMode) {
      setMockSaving(true);
      await simulateDelay(800);
      setMockSaving(false);
      toast.success(t("savedSuccess"));
      setHasChanges(false);
      return;
    }

    try {
      await updateMutation.mutateAsync({
        year: currentMonth.year,
        month: currentMonth.month,
        unavailableDates,
      });
      toast.success(t("savedSuccess"));
      setHasChanges(false);
    } catch {
      // Error is handled by the mutation hook
    }
  }, [selectedDates, currentMonth, updateMutation, t, selectedDepartmentId]);

  // Saving state
  const isSaving = isMockMode ? mockSaving : updateMutation.isPending;

  // Deadline info
  const isDeadlinePassed = typedDeadlineData?.isPassed ?? false;
  const deadlineDateFormatted = typedDeadlineData?.deadlineDate
    ? formatDeadlineDate(typedDeadlineData.deadlineDate)
    : undefined;

  // Combined loading state
  const isLoading = isLoadingAvailabilities || isLoadingDeadline;

  // Memoized selected dates count for current month
  const selectedCount = useMemo(() => {
    let count = 0;
    selectedDates.forEach((dateStr) => {
      const [y, m] = dateStr.split("-").map(Number);
      if (y === currentMonth.year && m === currentMonth.month) {
        count++;
      }
    });
    return count;
  }, [selectedDates, currentMonth]);

  // Loading state for departments
  if (isLoadingDepartments) {
    return (
      <div className="flex min-h-96 items-center justify-center">
        <div className="text-center">
          <IconLoader2 className="text-primary mx-auto mb-4 h-12 w-12 animate-spin" />
          <p className="text-muted-foreground">{tCommon("loading")}</p>
        </div>
      </div>
    );
  }

  // Error state for departments
  if (isDepartmentsError) {
    return (
      <div className="mx-auto max-w-2xl">
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-destructive">{tCommon("error")}</p>
            <p className="text-muted-foreground mt-2 text-sm">
              Impossible de charger les départements
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // No departments available
  if (departments.length === 0) {
    return (
      <div className="mx-auto max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>{t("title")}</CardTitle>
          </CardHeader>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              Vous n&apos;êtes membre d&apos;aucun département pour le moment.
            </p>
            <p className="text-muted-foreground mt-2 text-sm">
              Contactez un administrateur pour rejoindre un département.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("title")}</h1>
          <p className="text-muted-foreground">{t("selectDates")}</p>
        </div>

        {/* Save Button */}
        <Button
          onClick={handleSave}
          disabled={!hasChanges || isDeadlinePassed || isSaving || !selectedDepartmentId}
        >
          <IconDeviceFloppy className="mr-2 size-4" />
          {isSaving ? tCommon("loading") : tCommon("save")}
        </Button>
      </div>

      {/* Department Selector */}
      {departments.length > 1 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Département</CardTitle>
            <CardDescription>
              Sélectionnez le département pour lequel vous souhaitez gérer vos disponibilités
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select
              value={selectedDepartmentId ?? undefined}
              onValueChange={setSelectedDepartmentId}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {departments.map((dept) => (
                  <SelectItem key={dept.id} value={dept.id}>
                    {dept.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {isAvailabilityError && selectedDepartmentId && (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-destructive">{tCommon("error")}</p>
          </CardContent>
        </Card>
      )}

      {/* Calendar Card */}
      <Card>
        <CardHeader>
          <CardTitle>Calendrier</CardTitle>
          <CardDescription>
            Cliquez sur les jours où vous n&apos;êtes pas disponible
          </CardDescription>
        </CardHeader>
        <CardContent>
          <AvailabilityCalendar
            year={currentMonth.year}
            month={currentMonth.month}
            selectedDates={selectedDates}
            onDatesChange={handleDatesChange}
            onPreviousMonth={handlePreviousMonth}
            onNextMonth={handleNextMonth}
            isDeadlinePassed={isDeadlinePassed}
            deadlineDate={deadlineDateFormatted}
            isLoading={isLoading}
            isSaving={isSaving}
          />
        </CardContent>
      </Card>

      {/* Summary Card */}
      <Card size="sm">
        <CardContent className="flex items-center justify-between py-4">
          <div>
            <p className="text-sm font-medium">Résumé</p>
            <p className="text-muted-foreground text-sm">
              {selectedCount > 0 ? (
                <>
                  {selectedCount} jour{selectedCount > 1 ? "s" : ""} marqué
                  {selectedCount > 1 ? "s" : ""} comme indisponible
                  {selectedCount > 1 ? "s" : ""}
                </>
              ) : (
                "Aucune date sélectionnée"
              )}
            </p>
          </div>
          {hasChanges && !isDeadlinePassed && (
            <span className="text-primary text-sm font-medium">Modifications non enregistrées</span>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
