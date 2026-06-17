import { useAuthStore } from '../store/authStore';
import { authApi } from '../api';
import type { LoginRequest, UserCreate } from '../types';

/** Convenience hook wrapping the auth store + auth API. */
export function useAuth() {
  const { user, token, isAuthenticated, setAuth, setUser, logout } = useAuthStore();

  const login = async (payload: LoginRequest) => {
    const data = await authApi.login(payload);
    setAuth(data.access_token);
    // Token is now stored, so the axios interceptor will attach it here.
    try {
      const profile = await authApi.me();
      setUser(profile);
    } catch {
      // Profile fetch is best-effort; the session is still valid.
    }
    return data;
  };

  const register = (payload: UserCreate) => authApi.register(payload);

  return { user, token, isAuthenticated, login, register, logout };
}
