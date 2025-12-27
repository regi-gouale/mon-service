/**
 * UI Store
 * Global UI state management using Zustand
 */

import { create } from "zustand";
import { devtools } from "zustand/middleware";

export interface UIState {
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

  // Loading states
  globalLoading: boolean;

  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
  toggleSidebarCollapse: () => void;
  setSidebarCollapsed: (isCollapsed: boolean) => void;

  openModal: (modalId: string, data?: unknown) => void;
  closeModal: () => void;

  setNotificationCount: (count: number) => void;
  incrementNotificationCount: () => void;
  decrementNotificationCount: () => void;

  setTheme: (theme: "light" | "dark" | "system") => void;

  setGlobalLoading: (isLoading: boolean) => void;
}

export const useUIStore = create<UIState>()(
  devtools(
    (set): Omit<UIState, keyof UIState> & UIState => ({
      // Initial state
      isSidebarOpen: true,
      isSidebarCollapsed: false,
      activeModal: null,
      modalData: null,
      notificationCount: 0,
      theme: "system",
      globalLoading: false,

      // Sidebar actions
      toggleSidebar: () =>
        set((state) => ({
          isSidebarOpen: !state.isSidebarOpen,
        })),

      setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),

      toggleSidebarCollapse: () =>
        set((state) => ({
          isSidebarCollapsed: !state.isSidebarCollapsed,
        })),

      setSidebarCollapsed: (isCollapsed) => set({ isSidebarCollapsed: isCollapsed }),

      // Modal actions
      openModal: (modalId, data) =>
        set({
          activeModal: modalId,
          modalData: data,
        }),

      closeModal: () =>
        set({
          activeModal: null,
          modalData: null,
        }),

      // Notification actions
      setNotificationCount: (count) => set({ notificationCount: count }),

      incrementNotificationCount: () =>
        set((state) => ({
          notificationCount: state.notificationCount + 1,
        })),

      decrementNotificationCount: () =>
        set((state) => ({
          notificationCount: Math.max(0, state.notificationCount - 1),
        })),

      // Theme actions
      setTheme: (theme) => set({ theme }),

      // Loading actions
      setGlobalLoading: (isLoading) => set({ globalLoading: isLoading }),
    }),
    { name: "UIStore" }
  )
);
