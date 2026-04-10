import AsyncStorage from '@react-native-async-storage/async-storage';
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { loginApi, logoutApi, meApi, registerApi } from '../services/api/authApi';
import { normalizeApiError } from '../services/api/client';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isBootstrapping: true,
      error: null,
      signIn: async (credentials) => {
        set({ error: null });
        try {
          const result = await loginApi(credentials);
          set({ user: result.user, isAuthenticated: true });
          return { ok: true };
        } catch (error) {
          const message = normalizeApiError(error);
          set({ error: message });
          return { ok: false, message };
        }
      },
      signUp: async (payload) => {
        set({ error: null });
        try {
          const result = await registerApi(payload);
          set({ user: result.user, isAuthenticated: true });
          return { ok: true };
        } catch (error) {
          const message = normalizeApiError(error);
          set({ error: message });
          return { ok: false, message };
        }
      },
      bootstrapSession: async () => {
        try {
          const result = await meApi();
          set({ user: result.user, isAuthenticated: true, isBootstrapping: false });
        } catch (error) {
          set({ user: null, isAuthenticated: false, isBootstrapping: false });
        }
      },
      signOut: async () => {
        try {
          await logoutApi();
        } catch (error) {
          // Ignore network logout errors; local session must still clear.
        }
        set({ user: null, isAuthenticated: false, error: null });
      }
    }),
    {
      name: 'healthtwin-auth',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
      onRehydrateStorage: () => (state) => {
        if (state) state.isBootstrapping = false;
      }
    }
  )
);
