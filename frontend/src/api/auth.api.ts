import { apiClient } from './axios';
import type { LoginRequest, LoginResponse, UserCreate, MessageResponse } from '../types';

export const authApi = {
  register: (payload: UserCreate) =>
    apiClient.post<MessageResponse>('/auth/register', payload).then((r) => r.data),

  login: (payload: LoginRequest) =>
    apiClient.post<LoginResponse>('/auth/login', payload).then((r) => r.data),
};
