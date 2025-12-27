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
  useAvailabilityDeadline,
  useMyAvailabilities,
  useUpdateMyAvailabilities,
} from "@/hooks/useQuery";
import type { AvailabilityDeadlineResponse, MemberAvailabilityResponse } from "@/types";
import { IconDeviceFloppy } from "@tabler/icons-react";
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

export default function AvailabilityPage() {
  const t = useTranslations("Availability");
  const tCommon = useTranslations("Common");

  // TODO: Get departmentId from URL params or user context
  // For now, we'll use a placeholder
  const departmentId = "default-department";

  // Current displayed month
  const [currentMonth, setCurrentMonth] = useState<MonthYear>(getCurrentMonthYear);

  // Selected unavailable dates
  const [selectedDates, setSelectedDates] = useState<Set<string>>(new Set());

  // Track if there are unsaved changes
  const [hasChanges, setHasChanges] = useState(false);

  // Fetch current availabilities
  const {
    data: availabilityData,
    isLoading: isLoadingAvailabilities,
    isError: isAvailabilityError,
  } = useMyAvailabilities(departmentId, currentMonth.year, currentMonth.month);

  // Fetch deadline info
  const { data: deadlineData, isLoading: isLoadingDeadline } = useAvailabilityDeadline(
    departmentId,
    currentMonth.year,
    currentMonth.month
  );

  // Mutation for saving availabilities
  const updateMutation = useUpdateMyAvailabilities(departmentId);

  // Type-safe accessors
  const typedAvailabilityData = availabilityData as MemberAvailabilityResponse | undefined;
  const typedDeadlineData = deadlineData as AvailabilityDeadlineResponse | undefined;

  // Initialize selected dates from fetched data
  useEffect(() => {
    if (typedAvailabilityData?.unavailableDates) {
      const dates = new Set(typedAvailabilityData.unavailableDates.map((d) => d.date));
      setSelectedDates(dates);
      setHasChanges(false);
    }
  }, [typedAvailabilityData]);

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
  }, [selectedDates, currentMonth, updateMutation, t]);

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
          disabled={!hasChanges || isDeadlinePassed || updateMutation.isPending}
        >
          <IconDeviceFloppy className="mr-2 size-4" />
          {updateMutation.isPending ? tCommon("loading") : tCommon("save")}
        </Button>
      </div>

      {/* Error State */}
      {isAvailabilityError && (
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
            isSaving={updateMutation.isPending}
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
