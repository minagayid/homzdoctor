import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types';
import { STORAGE_KEYS } from '../lib/constants';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user?: User | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

/** Persisted auth state (token + user), synced to localStorage. */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setAuth: (token, user = null) => set({ token, user, isAuthenticated: true }),
      setUser: (user) => set({ user }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    { name: STORAGE_KEYS.auth },
  ),
);
