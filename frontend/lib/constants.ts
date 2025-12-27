/**
 * Application Constants
 * Centralized configuration values and constants
 */

// API Configuration
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const API_VERSION = "v1";
export const API_BASE_PATH = `/api/${API_VERSION}`;

// Authentication
export const TOKEN_STORAGE_KEY = "accessToken";
export const REFRESH_TOKEN_STORAGE_KEY = "refreshToken";
export const TOKEN_EXPIRY_BUFFER = 60; // seconds before expiry to refresh

// Application Routes
export const ROUTES = {
  // Public routes
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",

  // Protected routes
  DASHBOARD: "/dashboard",
  AVAILABILITY: "/availability",
  PLANNING: "/planning",
  TEAM: "/team",
  NOTIFICATIONS: "/notifications",
  PROFILE: "/profile",
  SETTINGS: "/settings",
} as const;

// API Endpoints
export const ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_BASE_PATH}/auth/login`,
    REGISTER: `${API_BASE_PATH}/auth/register`,
    LOGOUT: `${API_BASE_PATH}/auth/logout`,
    REFRESH: `${API_BASE_PATH}/auth/refresh`,
    FORGOT_PASSWORD: `${API_BASE_PATH}/auth/forgot-password`,
    RESET_PASSWORD: `${API_BASE_PATH}/auth/reset-password`,
    VERIFY_EMAIL: `${API_BASE_PATH}/auth/verify-email`,
    GOOGLE: `${API_BASE_PATH}/auth/google`,
  },
  USERS: {
    ME: `${API_BASE_PATH}/users/me`,
    UPDATE_PROFILE: `${API_BASE_PATH}/users/me`,
    UPLOAD_AVATAR: `${API_BASE_PATH}/users/me/avatar`,
    DATA_EXPORT: `${API_BASE_PATH}/users/me/data-export`,
  },
  DEPARTMENTS: `${API_BASE_PATH}/departments`,
  MEMBERS: `${API_BASE_PATH}/members`,
  AVAILABILITIES: `${API_BASE_PATH}/availabilities`,
  PLANNINGS: `${API_BASE_PATH}/plannings`,
  SERVICES: `${API_BASE_PATH}/services`,
  NOTIFICATIONS: `${API_BASE_PATH}/notifications`,
} as const;

// Date & Time
export const DATE_FORMAT = "yyyy-MM-dd";
export const DATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss";
export const DISPLAY_DATE_FORMAT = "dd/MM/yyyy";
export const DISPLAY_DATETIME_FORMAT = "dd/MM/yyyy HH:mm";

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// File Upload
export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

// Notification Types
export const NOTIFICATION_TYPES = {
  PLANNING_PUBLISHED: "planning_published",
  NEW_ASSIGNMENT: "new_assignment",
  MEMBER_JOINED: "member_joined",
  SERVICE_REMINDER: "service_reminder",
  AVAILABILITY_DEADLINE: "availability_deadline",
} as const;

// Planning Status
export const PLANNING_STATUS = {
  DRAFT: "draft",
  GENERATING: "generating",
  PUBLISHED: "published",
  ARCHIVED: "archived",
} as const;

// Member Roles
export const MEMBER_ROLES = {
  ADMIN: "admin",
  LEADER: "leader",
  MEMBER: "member",
} as const;

// WebSocket Events
export const WS_EVENTS = {
  AVAILABILITY_UPDATED: "availability:updated",
  PLANNING_GENERATION_PROGRESS: "planning:generation:progress",
  PLANNING_ASSIGNMENT_UPDATED: "planning:assignment:updated",
  PLANNING_PUBLISHED: "planning:published",
  NOTIFICATION_NEW: "notification:new",
  NOTIFICATION_COUNT: "notification:count",
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: "Erreur de connexion au serveur",
  UNAUTHORIZED: "Vous devez être connecté pour accéder à cette page",
  FORBIDDEN: "Vous n'avez pas les permissions nécessaires",
  NOT_FOUND: "Ressource non trouvée",
  SERVER_ERROR: "Erreur serveur, veuillez réessayer plus tard",
  VALIDATION_ERROR: "Erreur de validation des données",
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: "Connexion réussie",
  GOOGLE_LOGIN_SUCCESS: "Connexion avec Google réussie",
  REGISTER_SUCCESS: "Inscription réussie",
  PROFILE_UPDATED: "Profil mis à jour",
  AVAILABILITY_SAVED: "Disponibilités enregistrées",
  PLANNING_GENERATED: "Planning généré avec succès",
  PLANNING_PUBLISHED: "Planning publié",
} as const;
