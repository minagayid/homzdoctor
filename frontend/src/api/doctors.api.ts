import { apiClient } from './axios';

export interface DoctorDashboardStats {
  pendingReviews: number;
  reviewedRecords: number;
  totalRecords: number;
  patients: number;
  pendingPrescriptions: number;
}

export interface PendingRecord {
  id: number;
  patientId: number;
  patientName?: string;
  patientEmail?: string;
  recordType: string;
  filePath: string;
  findings?: string;
  diagnosis?: string;
  confidenceScore?: number;
  doctorReviewed: boolean;
  doctorNotes?: string;
  status: string;
  createdAt: string;
}

export interface ReviewAction {
  action: 'approve' | 'modify' | 'reject';
  notes?: string;
  diagnosis?: string;
  findings?: string;
}

export const doctorsApi = {
  dashboard: () => apiClient.get<DoctorDashboardStats>('/doctors/dashboard').then((r) => r.data),

  pendingReviews: () =>
    apiClient.get<PendingRecord[]>('/doctors/records/pending').then((r) => r.data),

  review: (recordId: number, payload: ReviewAction) =>
    apiClient.post<PendingRecord>(`/doctors/review/${recordId}`, payload).then((r) => r.data),
};
