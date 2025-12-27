/**
 * AvailabilityCalendar Component
 *
 * A month-view calendar that allows users to select multiple dates
 * for marking their unavailability. Supports:
 * - Multiple date selection
 * - Past dates marked as non-selectable
 * - Deadline indication
 * - Keyboard navigation
 */

"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { IconCalendarOff, IconChevronLeft, IconChevronRight } from "@tabler/icons-react";
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

interface DayInfo {
  date: Date;
  dayOfMonth: number;
  dateString: string;
  isCurrentMonth: boolean;
  isPast: boolean;
  isToday: boolean;
  isSelected: boolean;
  isDisabled: boolean;
}

// ============================================================================
// Helpers
// ============================================================================

const DAYS_OF_WEEK = ["L", "M", "M", "J", "V", "S", "D"] as const;

/**
 * Get the first day of the month
 */
function getFirstDayOfMonth(year: number, month: number): Date {
  return new Date(year, month - 1, 1);
}

/**
 * Get the last day of the month
 */
function getLastDayOfMonth(year: number, month: number): Date {
  return new Date(year, month, 0);
}

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
 * Check if two dates are the same day
 */
function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}

/**
 * Get month name in French
 */
function getMonthName(month: number): string {
  const months = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
  ];
  return months[month - 1] || "";
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
  const tCommon = useTranslations("Common");
  const today = useMemo(() => new Date(), []);

  // Generate calendar days for the current month view
  const calendarDays = useMemo((): DayInfo[] => {
    const days: DayInfo[] = [];
    const firstDay = getFirstDayOfMonth(year, month);
    const lastDay = getLastDayOfMonth(year, month);

    // Get day of week for first day (0 = Sunday, adjust to Monday = 0)
    let startDayOfWeek = firstDay.getDay();
    startDayOfWeek = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1;

    // Add days from previous month to fill the first week
    const prevMonthLastDay = new Date(year, month - 1, 0);
    for (let i = startDayOfWeek - 1; i >= 0; i--) {
      const date = new Date(year, month - 2, prevMonthLastDay.getDate() - i);
      const dateString = formatDateISO(date);
      days.push({
        date,
        dayOfMonth: date.getDate(),
        dateString,
        isCurrentMonth: false,
        isPast: date < today && !isSameDay(date, today),
        isToday: isSameDay(date, today),
        isSelected: selectedDates.has(dateString),
        isDisabled: true, // Previous month days are always disabled
      });
    }

    // Add current month days
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month - 1, day);
      const dateString = formatDateISO(date);
      const isPast = date < today && !isSameDay(date, today);
      days.push({
        date,
        dayOfMonth: day,
        dateString,
        isCurrentMonth: true,
        isPast,
        isToday: isSameDay(date, today),
        isSelected: selectedDates.has(dateString),
        isDisabled: isPast || isDeadlinePassed,
      });
    }

    // Add days from next month to complete the grid (6 rows x 7 days = 42)
    const remainingDays = 42 - days.length;
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(year, month, day);
      const dateString = formatDateISO(date);
      days.push({
        date,
        dayOfMonth: day,
        dateString,
        isCurrentMonth: false,
        isPast: false,
        isToday: isSameDay(date, today),
        isSelected: selectedDates.has(dateString),
        isDisabled: true, // Next month days are always disabled
      });
    }

    return days;
  }, [year, month, selectedDates, today, isDeadlinePassed]);

  // Handle day click
  const handleDayClick = useCallback(
    (day: DayInfo) => {
      if (day.isDisabled || !day.isCurrentMonth) return;

      const newDates = new Set(selectedDates);
      if (newDates.has(day.dateString)) {
        newDates.delete(day.dateString);
      } else {
        newDates.add(day.dateString);
      }
      onDatesChange(newDates);
    },
    [selectedDates, onDatesChange]
  );

  // Handle keyboard navigation
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent, day: DayInfo) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        handleDayClick(day);
      }
    },
    [handleDayClick]
  );

  // Selected count
  const selectedCount = useMemo(() => {
    // Count only dates from current month
    let count = 0;
    selectedDates.forEach((dateStr) => {
      const [y, m] = dateStr.split("-").map(Number);
      if (y === year && m === month) {
        count++;
      }
    });
    return count;
  }, [selectedDates, year, month]);

  return (
    <div className={cn("flex flex-col gap-4", className)}>
      {/* Header with month navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          size="icon"
          onClick={onPreviousMonth}
          disabled={isLoading || isSaving}
          aria-label={tCommon("previous")}
        >
          <IconChevronLeft className="size-5" />
        </Button>

        <h2 className="text-lg font-semibold">
          {getMonthName(month)} {year}
        </h2>

        <Button
          variant="ghost"
          size="icon"
          onClick={onNextMonth}
          disabled={isLoading || isSaving}
          aria-label={tCommon("next")}
        >
          <IconChevronRight className="size-5" />
        </Button>
      </div>

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

      {/* Calendar grid */}
      <div className="overflow-hidden rounded-lg border">
        {/* Day headers */}
        <div className="bg-muted grid grid-cols-7 border-b">
          {DAYS_OF_WEEK.map((day, index) => (
            <div key={index} className="text-muted-foreground py-2 text-center text-sm font-medium">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar days */}
        {isLoading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="border-primary h-8 w-8 animate-spin rounded-full border-b-2" />
          </div>
        ) : (
          <div className="grid grid-cols-7">
            {calendarDays.map((day, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleDayClick(day)}
                onKeyDown={(e) => handleKeyDown(e, day)}
                disabled={day.isDisabled}
                tabIndex={day.isCurrentMonth && !day.isDisabled ? 0 : -1}
                aria-label={`${day.dayOfMonth} ${getMonthName(month)} ${year}${day.isSelected ? " - Indisponible" : ""}`}
                aria-pressed={day.isSelected}
                className={cn(
                  "relative flex aspect-square items-center justify-center text-sm transition-colors",
                  "focus-visible:ring-ring focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none",
                  // Current month styling
                  day.isCurrentMonth ? "text-foreground" : "text-muted-foreground/50",
                  // Past day styling
                  day.isPast && "text-muted-foreground/40",
                  // Today styling
                  day.isToday && !day.isSelected && "font-bold ring-1 ring-current ring-inset",
                  // Selected styling
                  day.isSelected &&
                    day.isCurrentMonth &&
                    "bg-destructive text-destructive-foreground font-semibold",
                  // Hover styling for selectable days
                  !day.isDisabled &&
                    day.isCurrentMonth &&
                    !day.isSelected &&
                    "hover:bg-muted cursor-pointer",
                  // Disabled styling
                  day.isDisabled && "cursor-not-allowed opacity-50"
                )}
              >
                {day.dayOfMonth}
              </button>
            ))}
          </div>
        )}
      </div>

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
