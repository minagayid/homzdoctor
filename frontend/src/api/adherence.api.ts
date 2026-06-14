import { apiClient } from './axios';
import type { MedicationAdherence, MessageResponse } from '../types';

export const adherenceApi = {
  log: (adherence: Partial<MedicationAdherence>) =>
    apiClient.post<MessageResponse>('/adherence/log', adherence).then((r) => r.data),

  history: (patientId: number) =>
    apiClient.get(`/adherence/patient/${patientId}`).then((r) => r.data),

  score: (patientId: number) =>
    apiClient.get(`/adherence/patient/${patientId}/score`).then((r) => r.data),
};
