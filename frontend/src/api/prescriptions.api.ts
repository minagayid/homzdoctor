import { apiClient } from './axios';
import type { Prescription } from '../types';

export interface PrescriptionCreate {
  patientId: number;
  recordId: number;
  medications: Array<Record<string, unknown>>;
}

export const prescriptionsApi = {
  list: () => apiClient.get<Prescription[]>('/prescriptions').then((r) => r.data),

  getById: (id: number) =>
    apiClient.get<Prescription>(`/prescriptions/${id}`).then((r) => r.data),

  create: (payload: PrescriptionCreate) =>
    apiClient.post<Prescription>('/prescriptions', payload).then((r) => r.data),

  approve: (id: number) =>
    apiClient.put<Prescription>(`/prescriptions/${id}/approve`).then((r) => r.data),
};
