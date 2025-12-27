/**
 * Global TypeScript Types and Interfaces
 */

// User types
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatarUrl?: string;
  role: UserRole;
  organizationId: string;
  isEmailVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

export type UserRole = "admin" | "leader" | "member";

// Organization types
export interface Organization {
  id: string;
  name: string;
  slug: string;
  logoUrl?: string;
  createdAt: string;
  updatedAt: string;
}

// Department types
export interface Department {
  id: string;
  name: string;
  description?: string;
  organizationId: string;
  availabilityDeadline: number; // day of month
  createdAt: string;
  updatedAt: string;
}

// Member types
export interface Member {
  id: string;
  userId: string;
  departmentId: string;
  role: UserRole;
  skills: string[];
  user?: User;
  department?: Department;
  createdAt: string;
  updatedAt: string;
}

// Availability types
export interface Availability {
  id: string;
  memberId: string;
  date: string;
  isAvailable: boolean;
  reason?: string;
  member?: Member;
  createdAt: string;
  updatedAt: string;
}

// Availability API types
export interface UnavailableDate {
  date: string;
  reason?: string;
  isAllDay: boolean;
  startTime?: string;
  endTime?: string;
}

export interface SetAvailabilitiesRequest {
  year: number;
  month: number;
  unavailableDates: UnavailableDate[];
}

export interface MemberAvailabilityResponse {
  memberId: string;
  memberName: string;
  year: number;
  month: number;
  unavailableDates: UnavailableDate[];
}

export interface MemberAvailabilitySummary {
  memberId: string;
  memberName: string;
  unavailableDates: string[];
  totalUnavailableDays: number;
}

export interface DepartmentAvailabilityResponse {
  departmentId: string;
  departmentName: string;
  year: number;
  month: number;
  members: MemberAvailabilitySummary[];
}

export interface AvailabilityDeadlineResponse {
  departmentId: string;
  year: number;
  month: number;
  deadlineDate: string;
  isPassed: boolean;
  daysUntilDeadline: number;
}

// Service types
export interface Service {
  id: string;
  departmentId: string;
  name: string;
  description?: string;
  date: string;
  startTime: string;
  endTime: string;
  requiredMembers: number;
  dressCodeId?: string;
  dressCode?: DressCode;
  createdAt: string;
  updatedAt: string;
}

// Planning types
export interface Planning {
  id: string;
  departmentId: string;
  month: string; // YYYY-MM format
  status: PlanningStatus;
  confidenceScore?: number;
  notes?: string;
  department?: Department;
  assignments?: PlanningAssignment[];
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;
}

export type PlanningStatus = "draft" | "generating" | "published" | "archived";

export interface PlanningAssignment {
  id: string;
  planningId: string;
  serviceId: string;
  memberId: string;
  position?: string;
  notes?: string;
  service?: Service;
  member?: Member;
  createdAt: string;
  updatedAt: string;
}

// DressCode types
export interface DressCode {
  id: string;
  departmentId: string;
  name: string;
  description?: string;
  imageUrls: string[];
  createdAt: string;
  updatedAt: string;
}

// Notification types
export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  data?: Record<string, unknown>;
  isRead: boolean;
  createdAt: string;
  readAt?: string;
}

export type NotificationType =
  | "planning_published"
  | "new_assignment"
  | "member_joined"
  | "service_reminder"
  | "availability_deadline";

// Invitation types
export interface Invitation {
  id: string;
  departmentId: string;
  email: string;
  role: UserRole;
  token: string;
  expiresAt: string;
  acceptedAt?: string;
  createdAt: string;
}

// Report types
export interface ServiceReport {
  id: string;
  serviceId: string;
  memberId: string;
  notes: string;
  photoUrls: string[];
  service?: Service;
  member?: Member;
  createdAt: string;
  updatedAt: string;
}

// Inventory types
export interface InventoryItem {
  id: string;
  departmentId: string;
  name: string;
  description?: string;
  quantity: number;
  condition: ItemCondition;
  location?: string;
  photoUrls: string[];
  assignedToId?: string;
  assignedTo?: Member;
  createdAt: string;
  updatedAt: string;
}

export type ItemCondition = "excellent" | "good" | "fair" | "needs_repair" | "broken";

// Event types
export interface Event {
  id: string;
  departmentId: string;
  type: EventType;
  title: string;
  description?: string;
  date: string;
  relatedUserId?: string;
  relatedUser?: User;
  createdAt: string;
  updatedAt: string;
}

export type EventType = "birthday" | "trip" | "holiday" | "other";

// Shopping List types
export interface ShoppingList {
  id: string;
  departmentId: string;
  name: string;
  description?: string;
  items?: ShoppingItem[];
  createdAt: string;
  updatedAt: string;
}

export interface ShoppingItem {
  id: string;
  shoppingListId: string;
  name: string;
  quantity: number;
  unit?: string;
  isPurchased: boolean;
  purchasedBy?: string;
  purchasedAt?: string;
  createdAt: string;
  updatedAt: string;
}

// Pagination types
export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Form types
export interface FormState<T = unknown> {
  data: T;
  errors: Record<string, string>;
  isSubmitting: boolean;
  isDirty: boolean;
}

// API Response types
export interface ApiResponse<T = unknown> {
  data?: T;
  message?: string;
  error?: string;
}

export interface ApiErrorResponse {
  detail: string;
  status: number;
  errors?: Record<string, string[]>;
}
