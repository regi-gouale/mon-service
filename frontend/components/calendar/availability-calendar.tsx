/**
 * AvailabilityCalendar Component
 *
 * A month-view calendar that allows users to select multiple dates
 * for marking their unavailability. Uses shadcn Calendar component.
 * Supports:
 * - Multiple date selection
 * - Week number display
 * - Past dates marked as non-selectable
 * - Deadline indication
 */

"use client";

import { Calendar } from "@/components/ui/calendar";
import { cn } from "@/lib/utils";
import { IconCalendarOff } from "@tabler/icons-react";
import { fr } from "date-fns/locale";
import { useTranslations } from "next-intl";
import { useCallback, useMemo } from "react";

// ============================================================================
// Types
// ============================================================================

export interface AvailabilityCalendarProps {
  /** Currently displayed year */
  year: number;
  /** Currently displayed month (1-12) */
  month: number;
  /** Set of selected unavailable dates (ISO format YYYY-MM-DD) */
  selectedDates: Set<string>;
  /** Callback when dates selection changes */
  onDatesChange: (dates: Set<string>) => void;
  /** Callback to navigate to previous month */
  onPreviousMonth: () => void;
  /** Callback to navigate to next month */
  onNextMonth: () => void;
  /** Whether the deadline has passed (disables selection) */
  isDeadlinePassed?: boolean;
  /** Deadline date to display */
  deadlineDate?: string;
  /** Whether the component is in loading state */
  isLoading?: boolean;
  /** Whether the save operation is in progress */
  isSaving?: boolean;
  /** Additional CSS class names */
  className?: string;
}

// ============================================================================
// Helpers
// ============================================================================

/**
 * Format date to ISO string (YYYY-MM-DD)
 */
function formatDateISO(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/**
 * Parse ISO date string to Date object
 */
function parseDateISO(dateString: string): Date {
  const [year, month, day] = dateString.split("-").map(Number);
  return new Date(year, month - 1, day);
}

// ============================================================================
// Component
// ============================================================================

export function AvailabilityCalendar({
  year,
  month,
  selectedDates,
  onDatesChange,
  onPreviousMonth,
  onNextMonth,
  isDeadlinePassed = false,
  deadlineDate,
  isLoading = false,
  isSaving = false,
  className,
}: AvailabilityCalendarProps) {
  const t = useTranslations("Availability");
  const today = useMemo(() => new Date(), []);

  // Convert Set<string> to Date[] for the Calendar component
  const selectedDatesArray = useMemo(() => {
    return Array.from(selectedDates).map(parseDateISO);
  }, [selectedDates]);

  // Current displayed month as Date
  const displayedMonth = useMemo(() => {
    return new Date(year, month - 1, 1);
  }, [year, month]);

  // Handle date selection
  const handleSelect = useCallback(
    (dates: Date[] | undefined) => {
      if (!dates) {
        onDatesChange(new Set());
        return;
      }
      const newDates = new Set(dates.map(formatDateISO));
      onDatesChange(newDates);
    },
    [onDatesChange]
  );

  // Handle month change from Calendar navigation
  const handleMonthChange = useCallback(
    (newMonth: Date) => {
      const newYear = newMonth.getFullYear();
      const newMonthNum = newMonth.getMonth() + 1;
      const currentYear = year;
      const currentMonth = month;

      if (newYear < currentYear || (newYear === currentYear && newMonthNum < currentMonth)) {
        onPreviousMonth();
      } else if (newYear > currentYear || (newYear === currentYear && newMonthNum > currentMonth)) {
        onNextMonth();
      }
    },
    [year, month, onPreviousMonth, onNextMonth]
  );

  // Selected count for current month only
  const selectedCount = useMemo(() => {
    let count = 0;
    selectedDates.forEach((dateStr) => {
      const [y, m] = dateStr.split("-").map(Number);
      if (y === year && m === month) {
        count++;
      }
    });
    return count;
  }, [selectedDates, year, month]);

  // Handle week number click - select/deselect all days in the week
  const handleWeekNumberClick = useCallback(
    (_weekNumber: number, weekDates: Date[]) => {
      if (isDeadlinePassed) return;

      // Filter to only selectable days (current month and not past)
      const selectableDates = weekDates.filter((date) => {
        const isPast = date < today && date.toDateString() !== today.toDateString();
        const isCurrentMonth = date.getMonth() + 1 === month && date.getFullYear() === year;
        return isCurrentMonth && !isPast;
      });

      if (selectableDates.length === 0) return;

      const selectableDateStrings = selectableDates.map(formatDateISO);
      const allSelected = selectableDateStrings.every((dateStr) => selectedDates.has(dateStr));

      const newDates = new Set(selectedDates);
      if (allSelected) {
        // Deselect all days in the week
        selectableDateStrings.forEach((dateStr) => {
          newDates.delete(dateStr);
        });
      } else {
        // Select all days in the week
        selectableDateStrings.forEach((dateStr) => {
          newDates.add(dateStr);
        });
      }
      onDatesChange(newDates);
    },
    [selectedDates, onDatesChange, today, month, year, isDeadlinePassed]
  );

  return (
    <div className={cn("flex flex-col gap-4", className)}>
      {/* Deadline warning */}
      {isDeadlinePassed && (
        <div className="flex items-center gap-2 rounded-lg bg-amber-100 px-4 py-2 text-amber-800 dark:bg-amber-900/30 dark:text-amber-200">
          <IconCalendarOff className="size-5 shrink-0" />
          <span className="text-sm">{t("deadlinePassed")}</span>
        </div>
      )}

      {/* Deadline info */}
      {deadlineDate && !isDeadlinePassed && (
        <div className="text-muted-foreground text-center text-sm">
          {t("deadline")}: {deadlineDate}
        </div>
      )}

      {/* Calendar using shadcn Calendar component */}
      {isLoading ? (
        <div className="flex h-64 items-center justify-center rounded-lg border">
          <div className="border-primary h-8 w-8 animate-spin rounded-full border-b-2" />
        </div>
      ) : (
        <Calendar
          mode="multiple"
          selected={selectedDatesArray}
          onSelect={handleSelect}
          month={displayedMonth}
          onMonthChange={handleMonthChange}
          locale={fr}
          weekStartsOn={1}
          showWeekNumber
          onWeekNumberClick={handleWeekNumberClick}
          disabled={(date) => {
            // Disable past dates and dates when deadline passed
            const isPast = date < today && date.toDateString() !== today.toDateString();
            return isPast || isDeadlinePassed;
          }}
          className="mx-auto w-lg rounded-lg border"
        />
      )}

      {/* Selection summary */}
      <div className="text-muted-foreground flex items-center justify-between text-sm">
        <span>
          {selectedCount > 0 ? (
            <>
              {selectedCount} jour{selectedCount > 1 ? "s" : ""} d&apos;indisponibilité
            </>
          ) : (
            t("noSelection")
          )}
        </span>
        {isSaving && <span className="text-primary animate-pulse">Enregistrement...</span>}
      </div>
    </div>
  );
}

export default AvailabilityCalendar;
