import { apiClient } from './axios';
import type { MessageResponse } from '../types';

export const appointmentsApi = {
  create: (data: Record<string, unknown>) =>
    apiClient.post<MessageResponse>('/appointments', data).then((r) => r.data),

  getById: (id: number) =>
    apiClient.get(`/appointments/${id}`).then((r) => r.data),

  cancel: (id: number) =>
    apiClient.put(`/appointments/${id}/cancel`).then((r) => r.data),
};
