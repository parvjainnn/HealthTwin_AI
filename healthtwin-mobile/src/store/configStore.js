import AsyncStorage from '@react-native-async-storage/async-storage';
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { setApiBaseUrl } from '../services/api/client';

const DEFAULT_API_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://10.0.2.2:5000';

export const useConfigStore = create(
  persist(
    (set) => ({
      apiBaseUrl: DEFAULT_API_URL,
      setApiUrl: (url) => {
        const sanitized = (url || '').trim().replace(/\/+$/, '');
        if (!sanitized) return;
        setApiBaseUrl(sanitized);
        set({ apiBaseUrl: sanitized });
      },
      hydrateApiUrl: (url) => {
        const sanitized = (url || DEFAULT_API_URL).trim().replace(/\/+$/, '');
        setApiBaseUrl(sanitized);
        set({ apiBaseUrl: sanitized });
      }
    }),
    {
      name: 'healthtwin-config',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({ apiBaseUrl: state.apiBaseUrl }),
      onRehydrateStorage: () => (state) => {
        if (state?.apiBaseUrl) {
          setApiBaseUrl(state.apiBaseUrl);
        }
      }
    }
  )
);
