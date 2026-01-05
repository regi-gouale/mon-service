/**
 * Mock Data for Frontend Development
 * This file contains all mock data used when the backend is not available
 */

// ============================================================================
// Types
// ============================================================================

export interface MockUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatarUrl?: string;
  role: "admin" | "leader" | "member";
  organizationId: string;
  isEmailVerified: boolean;
}

export interface MockTeam {
  id: string;
  name: string;
  description: string;
  color: string;
  members: MockTeamMember[];
  positions: string[];
}

export interface MockTeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar: string | null;
  status: "active" | "away" | "inactive";
  phone?: string;
  skills?: string[];
  joinedAt: string;
}

export interface MockService {
  id: string;
  date: string;
  name: string;
  time: string;
  endTime: string;
  teams: string[];
  confirmed: number;
  pending: number;
  status: "draft" | "published" | "completed";
  dressCode?: string;
  notes?: string;
}

export interface MockNotification {
  id: string;
  type: "assignment" | "reminder" | "announcement" | "availability" | "planning";
  title: string;
  message: string;
  isRead: boolean;
  createdAt: string;
  actionUrl?: string;
}

export interface MockAvailability {
  date: string;
  available: boolean;
  reason?: string;
}

// ============================================================================
// Mock Users
// ============================================================================

export const mockUsers: MockUser[] = [
  {
    id: "user-1",
    email: "admin@monservice.fr",
    firstName: "Marie",
    lastName: "Dupont",
    avatarUrl: undefined,
    role: "admin",
    organizationId: "org-1",
    isEmailVerified: true,
  },
  {
    id: "user-2",
    email: "leader@monservice.fr",
    firstName: "Pierre",
    lastName: "Martin",
    avatarUrl: undefined,
    role: "leader",
    organizationId: "org-1",
    isEmailVerified: true,
  },
  {
    id: "user-3",
    email: "membre@monservice.fr",
    firstName: "Sophie",
    lastName: "Bernard",
    avatarUrl: undefined,
    role: "member",
    organizationId: "org-1",
    isEmailVerified: true,
  },
];

export const currentMockUser = mockUsers[0];

// ============================================================================
// Mock Teams
// ============================================================================

export const mockTeams: MockTeam[] = [
  {
    id: "team-1",
    name: "Louange",
    description: "Équipe de louange et worship",
    color: "primary",
    members: [
      {
        id: "m1",
        name: "Marie Dupont",
        email: "marie@example.com",
        role: "Leader",
        avatar: null,
        status: "active",
        phone: "06 12 34 56 78",
        skills: ["Chant", "Piano"],
        joinedAt: "2024-01-15",
      },
      {
        id: "m2",
        name: "Pierre Martin",
        email: "pierre@example.com",
        role: "Chant",
        avatar: null,
        status: "active",
        phone: "06 23 45 67 89",
        skills: ["Chant"],
        joinedAt: "2024-02-20",
      },
      {
        id: "m3",
        name: "Sophie Bernard",
        email: "sophie@example.com",
        role: "Piano",
        avatar: null,
        status: "active",
        phone: "06 34 56 78 90",
        skills: ["Piano", "Clavier"],
        joinedAt: "2024-03-10",
      },
      {
        id: "m4",
        name: "Lucas Tremblay",
        email: "lucas@example.com",
        role: "Guitare",
        avatar: null,
        status: "away",
        skills: ["Guitare acoustique", "Guitare électrique"],
        joinedAt: "2024-04-05",
      },
      {
        id: "m5",
        name: "Emma Leroy",
        email: "emma@example.com",
        role: "Batterie",
        avatar: null,
        status: "active",
        skills: ["Batterie", "Percussions"],
        joinedAt: "2024-05-15",
      },
    ],
    positions: ["Leader", "Chant", "Piano", "Guitare", "Batterie", "Basse", "Clavier"],
  },
  {
    id: "team-2",
    name: "Technique",
    description: "Son, lumières et vidéo",
    color: "accent",
    members: [
      {
        id: "m6",
        name: "Hugo Bernard",
        email: "hugo@example.com",
        role: "Responsable",
        avatar: null,
        status: "active",
        skills: ["Son", "Mixage"],
        joinedAt: "2024-01-20",
      },
      {
        id: "m7",
        name: "Léa Martin",
        email: "lea@example.com",
        role: "Vidéo",
        avatar: null,
        status: "active",
        skills: ["Vidéo", "Streaming"],
        joinedAt: "2024-02-25",
      },
      {
        id: "m8",
        name: "Antoine Dubois",
        email: "antoine@example.com",
        role: "Lumières",
        avatar: null,
        status: "active",
        skills: ["Éclairage"],
        joinedAt: "2024-03-30",
      },
    ],
    positions: ["Responsable", "Son", "Vidéo", "Lumières", "Streaming", "Régie"],
  },
  {
    id: "team-3",
    name: "Accueil",
    description: "Accueil et hospitalité",
    color: "success",
    members: [
      {
        id: "m9",
        name: "Julie Moreau",
        email: "julie@example.com",
        role: "Responsable",
        avatar: null,
        status: "active",
        skills: ["Accueil", "Communication"],
        joinedAt: "2024-01-10",
      },
      {
        id: "m10",
        name: "Thomas Petit",
        email: "thomas@example.com",
        role: "Accueil",
        avatar: null,
        status: "active",
        skills: ["Accueil"],
        joinedAt: "2024-02-15",
      },
      {
        id: "m11",
        name: "Clara Roux",
        email: "clara@example.com",
        role: "Accueil",
        avatar: null,
        status: "active",
        skills: ["Accueil", "Café"],
        joinedAt: "2024-03-20",
      },
      {
        id: "m12",
        name: "Nicolas Laurent",
        email: "nicolas@example.com",
        role: "Parking",
        avatar: null,
        status: "away",
        skills: ["Parking", "Sécurité"],
        joinedAt: "2024-04-25",
      },
    ],
    positions: ["Responsable", "Accueil", "Parking", "Café", "Vestiaire"],
  },
  {
    id: "team-4",
    name: "Enfants",
    description: "Ministère des enfants (3-12 ans)",
    color: "warning",
    members: [
      {
        id: "m13",
        name: "Céline Richard",
        email: "celine@example.com",
        role: "Responsable",
        avatar: null,
        status: "active",
        skills: ["Animation", "Pédagogie"],
        joinedAt: "2024-01-05",
      },
      {
        id: "m14",
        name: "François Simon",
        email: "francois@example.com",
        role: "Animateur",
        avatar: null,
        status: "active",
        skills: ["Animation", "Musique"],
        joinedAt: "2024-02-10",
      },
      {
        id: "m15",
        name: "Isabelle Morel",
        email: "isabelle@example.com",
        role: "Animateur",
        avatar: null,
        status: "active",
        skills: ["Animation", "Arts plastiques"],
        joinedAt: "2024-03-15",
      },
    ],
    positions: ["Responsable", "Animateur", "Assistant", "Nursery"],
  },
  {
    id: "team-5",
    name: "Intercession",
    description: "Équipe de prière et intercession",
    color: "info",
    members: [
      {
        id: "m16",
        name: "Paul Girard",
        email: "paul@example.com",
        role: "Responsable",
        avatar: null,
        status: "active",
        skills: ["Prière", "Écoute"],
        joinedAt: "2024-01-25",
      },
      {
        id: "m17",
        name: "Anne Fournier",
        email: "anne@example.com",
        role: "Intercesseur",
        avatar: null,
        status: "active",
        skills: ["Prière"],
        joinedAt: "2024-02-28",
      },
    ],
    positions: ["Responsable", "Intercesseur"],
  },
];

// ============================================================================
// Mock Services
// ============================================================================

export const mockServices: MockService[] = [
  {
    id: "service-1",
    date: "2026-01-11",
    name: "Culte du dimanche matin",
    time: "10:00",
    endTime: "12:00",
    teams: ["Louange", "Technique", "Accueil", "Enfants"],
    confirmed: 12,
    pending: 3,
    status: "published",
    dressCode: "Tenue de ville élégante",
    notes: "Sainte Cène ce dimanche",
  },
  {
    id: "service-2",
    date: "2026-01-11",
    name: "Culte du dimanche soir",
    time: "18:00",
    endTime: "20:00",
    teams: ["Louange", "Technique"],
    confirmed: 6,
    pending: 1,
    status: "published",
    dressCode: "Tenue décontractée",
  },
  {
    id: "service-3",
    date: "2026-01-14",
    name: "Réunion de prière",
    time: "19:30",
    endTime: "21:00",
    teams: ["Intercession"],
    confirmed: 5,
    pending: 0,
    status: "published",
  },
  {
    id: "service-4",
    date: "2026-01-18",
    name: "Culte du dimanche matin",
    time: "10:00",
    endTime: "12:00",
    teams: ["Louange", "Technique", "Accueil", "Enfants"],
    confirmed: 8,
    pending: 6,
    status: "published",
    dressCode: "Tenue de ville élégante",
  },
  {
    id: "service-5",
    date: "2026-01-25",
    name: "Culte du dimanche matin",
    time: "10:00",
    endTime: "12:00",
    teams: ["Louange", "Technique", "Accueil", "Enfants"],
    confirmed: 4,
    pending: 10,
    status: "draft",
  },
  {
    id: "service-6",
    date: "2026-02-01",
    name: "Culte du dimanche matin",
    time: "10:00",
    endTime: "12:00",
    teams: ["Louange", "Technique", "Accueil", "Enfants"],
    confirmed: 0,
    pending: 0,
    status: "draft",
  },
];

// ============================================================================
// Mock Notifications
// ============================================================================

export const mockNotifications: MockNotification[] = [
  {
    id: "notif-1",
    type: "assignment",
    title: "Nouvelle affectation",
    message: "Vous avez été affecté au service du 11 janvier - Louange",
    isRead: false,
    createdAt: "2026-01-05T10:30:00Z",
    actionUrl: "/dashboard/planning",
  },
  {
    id: "notif-2",
    type: "reminder",
    title: "Rappel de service",
    message: "N'oubliez pas : culte du dimanche demain à 10h00",
    isRead: false,
    createdAt: "2026-01-04T18:00:00Z",
  },
  {
    id: "notif-3",
    type: "availability",
    title: "Saisie des disponibilités",
    message: "N'oubliez pas de saisir vos disponibilités pour février avant le 20 janvier",
    isRead: false,
    createdAt: "2026-01-03T09:00:00Z",
    actionUrl: "/dashboard/availability",
  },
  {
    id: "notif-4",
    type: "announcement",
    title: "Annonce de l'équipe",
    message: "Réunion d'équipe exceptionnelle le 15 janvier à 20h",
    isRead: true,
    createdAt: "2026-01-02T14:30:00Z",
  },
  {
    id: "notif-5",
    type: "planning",
    title: "Planning publié",
    message: "Le planning de janvier a été publié. Consultez vos affectations.",
    isRead: true,
    createdAt: "2026-01-01T08:00:00Z",
    actionUrl: "/dashboard/planning",
  },
  {
    id: "notif-6",
    type: "assignment",
    title: "Modification d'affectation",
    message: "Votre rôle a été modifié pour le service du 18 janvier",
    isRead: true,
    createdAt: "2025-12-30T11:00:00Z",
  },
];

// ============================================================================
// Mock Availabilities
// ============================================================================

export const mockAvailabilities: MockAvailability[] = [
  { date: "2026-01-15", available: false, reason: "Vacances" },
  { date: "2026-01-16", available: false, reason: "Vacances" },
  { date: "2026-01-17", available: false, reason: "Vacances" },
  { date: "2026-01-22", available: false, reason: "Rendez-vous médical" },
];

// ============================================================================
// Mock Planning Assignments
// ============================================================================

export interface MockPlanningAssignment {
  id: string;
  serviceId: string;
  memberId: string;
  memberName: string;
  teamId: string;
  teamName: string;
  position: string;
  status: "confirmed" | "pending" | "declined";
  confirmedAt?: string;
}

export const mockPlanningAssignments: MockPlanningAssignment[] = [
  {
    id: "assign-1",
    serviceId: "service-1",
    memberId: "m1",
    memberName: "Marie Dupont",
    teamId: "team-1",
    teamName: "Louange",
    position: "Leader",
    status: "confirmed",
    confirmedAt: "2026-01-03T10:00:00Z",
  },
  {
    id: "assign-2",
    serviceId: "service-1",
    memberId: "m2",
    memberName: "Pierre Martin",
    teamId: "team-1",
    teamName: "Louange",
    position: "Chant",
    status: "confirmed",
    confirmedAt: "2026-01-03T11:00:00Z",
  },
  {
    id: "assign-3",
    serviceId: "service-1",
    memberId: "m3",
    memberName: "Sophie Bernard",
    teamId: "team-1",
    teamName: "Louange",
    position: "Piano",
    status: "pending",
  },
  {
    id: "assign-4",
    serviceId: "service-1",
    memberId: "m6",
    memberName: "Hugo Bernard",
    teamId: "team-2",
    teamName: "Technique",
    position: "Son",
    status: "confirmed",
    confirmedAt: "2026-01-02T15:00:00Z",
  },
  {
    id: "assign-5",
    serviceId: "service-1",
    memberId: "m9",
    memberName: "Julie Moreau",
    teamId: "team-3",
    teamName: "Accueil",
    position: "Responsable",
    status: "confirmed",
    confirmedAt: "2026-01-02T16:00:00Z",
  },
];

// ============================================================================
// Mock Activity
// ============================================================================

export interface MockActivity {
  id: string;
  type: "confirmed" | "declined" | "modified" | "created";
  user: string;
  action: string;
  time: string;
  serviceId?: string;
}

export const mockRecentActivity: MockActivity[] = [
  {
    id: "act-1",
    type: "confirmed",
    user: "Marie D.",
    action: "a confirmé sa disponibilité pour le 11 janvier",
    time: "Il y a 2h",
    serviceId: "service-1",
  },
  {
    id: "act-2",
    type: "declined",
    user: "Pierre M.",
    action: "n'est pas disponible le 18 janvier",
    time: "Il y a 3h",
    serviceId: "service-4",
  },
  {
    id: "act-3",
    type: "confirmed",
    user: "Sophie B.",
    action: "a confirmé sa disponibilité pour le 11 janvier",
    time: "Il y a 5h",
    serviceId: "service-1",
  },
  {
    id: "act-4",
    type: "modified",
    user: "Admin",
    action: "a modifié le planning du 25 janvier",
    time: "Hier",
    serviceId: "service-5",
  },
  {
    id: "act-5",
    type: "created",
    user: "Admin",
    action: "a créé un nouveau service pour le 1er février",
    time: "Il y a 2 jours",
    serviceId: "service-6",
  },
];

// ============================================================================
// Mock Statistics
// ============================================================================

export const mockDashboardStats = {
  upcomingServices: 4,
  totalMembers: 17,
  pendingConfirmations: 10,
  teamsCount: 5,
  servicesThisMonth: 8,
  participationRate: 87,
};

// ============================================================================
// Mock Departments (for availability page)
// ============================================================================

export interface MockDepartment {
  id: string;
  name: string;
  description: string;
  color: string;
  memberCount: number;
}

export const mockDepartments: MockDepartment[] = [
  {
    id: "dept-1",
    name: "Louange",
    description: "Équipe de louange et adoration",
    color: "#3B82F6",
    memberCount: 12,
  },
  {
    id: "dept-2",
    name: "Accueil",
    description: "Équipe d'accueil des visiteurs",
    color: "#10B981",
    memberCount: 8,
  },
  {
    id: "dept-3",
    name: "Technique",
    description: "Équipe son et vidéo",
    color: "#8B5CF6",
    memberCount: 6,
  },
];

export interface MockAvailabilityDeadline {
  deadlineDate: string;
  isPassed: boolean;
  daysRemaining: number;
}

export interface MockUnavailableDate {
  date: string;
  isAllDay: boolean;
  reason?: string;
}

export interface MockMemberAvailability {
  memberId: string;
  departmentId: string;
  year: number;
  month: number;
  unavailableDates: MockUnavailableDate[];
}

// Generate mock availability for current month
export function getMockMyAvailabilities(
  departmentId: string,
  year: number,
  month: number
): MockMemberAvailability {
  // Generate some random unavailable dates
  const unavailableDates: MockUnavailableDate[] = [];
  const daysInMonth = new Date(year, month, 0).getDate();

  // Randomly mark 2-4 days as unavailable
  const unavailableCount = Math.floor(Math.random() * 3) + 2;
  const usedDays = new Set<number>();

  for (let i = 0; i < unavailableCount; i++) {
    let day: number;
    do {
      day = Math.floor(Math.random() * daysInMonth) + 1;
    } while (usedDays.has(day));
    usedDays.add(day);

    unavailableDates.push({
      date: `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`,
      isAllDay: true,
    });
  }

  return {
    memberId: currentMockUser.id,
    departmentId,
    year,
    month,
    unavailableDates: unavailableDates.sort((a, b) => a.date.localeCompare(b.date)),
  };
}

export function getMockAvailabilityDeadline(year: number, month: number): MockAvailabilityDeadline {
  // Deadline is 20th of previous month
  const deadlineMonth = month === 1 ? 12 : month - 1;
  const deadlineYear = month === 1 ? year - 1 : year;
  const deadlineDate = new Date(deadlineYear, deadlineMonth - 1, 20);
  const now = new Date();
  const isPassed = now > deadlineDate;
  const daysRemaining = Math.max(
    0,
    Math.ceil((deadlineDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  );

  return {
    deadlineDate: deadlineDate.toISOString(),
    isPassed,
    daysRemaining,
  };
}

// ============================================================================
// Helper to simulate API delay
// ============================================================================

export function simulateDelay(ms: number = 500): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ============================================================================
// Mock Authentication
// ============================================================================

export const mockCredentials = {
  email: "demo@monservice.fr",
  password: "demo1234",
};

export function validateMockLogin(email: string, password: string): MockUser | null {
  // Accept any email/password for demo purposes
  // In a real mock, you might want to be more strict
  if (email && password.length >= 4) {
    return {
      ...currentMockUser,
      email,
      firstName: email.split("@")[0].charAt(0).toUpperCase() + email.split("@")[0].slice(1),
    };
  }
  return null;
}
