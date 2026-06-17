import { apiClient } from './axios';
import type { LoginRequest, LoginResponse, UserCreate, User } from '../types';

export const authApi = {
  register: (payload: UserCreate) =>
    apiClient.post<User>('/auth/register', payload).then((r) => r.data),

  login: (payload: LoginRequest) =>
    apiClient.post<LoginResponse>('/auth/login', payload).then((r) => r.data),

  me: () => apiClient.get<User>('/auth/me').then((r) => r.data),
};
