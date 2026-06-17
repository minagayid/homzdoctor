import { apiClient } from './axios';
import type { Appointment } from '../types';

export interface AppointmentCreate {
  reason: string;
  scheduledTime: string;
}

export const appointmentsApi = {
  list: () => apiClient.get<Appointment[]>('/appointments').then((r) => r.data),

  getById: (id: number) =>
    apiClient.get<Appointment>(`/appointments/${id}`).then((r) => r.data),

  create: (payload: AppointmentCreate) =>
    apiClient.post<Appointment>('/appointments', payload).then((r) => r.data),

  cancel: (id: number) =>
    apiClient.put<Appointment>(`/appointments/${id}/cancel`).then((r) => r.data),
};
