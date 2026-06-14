import { useAuthStore } from '../store/authStore';
import { authApi } from '../api';
import type { LoginRequest, UserCreate } from '../types';

/** Convenience hook wrapping the auth store + auth API. */
export function useAuth() {
  const { user, token, isAuthenticated, setAuth, logout } = useAuthStore();

  const login = async (payload: LoginRequest) => {
    const data = await authApi.login(payload);
    setAuth(data.access_token);
    return data;
  };

  const register = (payload: UserCreate) => authApi.register(payload);

  return { user, token, isAuthenticated, login, register, logout };
}
