import { apiClient } from './axios';
import type { DoctorReview, MessageResponse } from '../types';

export const doctorsApi = {
  review: (recordId: number, review: Partial<DoctorReview>) =>
    apiClient.post<MessageResponse>(`/doctors/review/${recordId}`, review).then((r) => r.data),

  dashboard: () => apiClient.get('/doctors/dashboard').then((r) => r.data),
};
