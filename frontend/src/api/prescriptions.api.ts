import { apiClient } from './axios';
import type { Prescription, MessageResponse } from '../types';

export const prescriptionsApi = {
  create: (prescription: Partial<Prescription>) =>
    apiClient.post<MessageResponse>('/prescriptions', prescription).then((r) => r.data),

  getById: (id: number) =>
    apiClient.get(`/prescriptions/${id}`).then((r) => r.data),

  approve: (id: number) =>
    apiClient.put(`/prescriptions/${id}/approve`).then((r) => r.data),
};
