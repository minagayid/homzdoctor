import { apiClient } from './axios';
import type { MedicalRecord, MessageResponse } from '../types';

export interface MedicalRecordCreate {
  recordType: string;
  filePath: string;
  findings?: string;
  diagnosis?: string;
}

export type MedicalRecordUpdate = Partial<MedicalRecordCreate>;

export const recordsApi = {
  list: () => apiClient.get<MedicalRecord[]>('/medical/records').then((r) => r.data),

  getById: (id: number) =>
    apiClient.get<MedicalRecord>(`/medical/records/${id}`).then((r) => r.data),

  create: (payload: MedicalRecordCreate) =>
    apiClient.post<MedicalRecord>('/medical/records', payload).then((r) => r.data),

  update: (id: number, payload: MedicalRecordUpdate) =>
    apiClient.put<MedicalRecord>(`/medical/records/${id}`, payload).then((r) => r.data),

  remove: (id: number) =>
    apiClient.delete<void>(`/medical/records/${id}`).then((r) => r.data),

  uploadFile: (recordId: number, file: File) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient
      .post<MessageResponse>(`/medical/records/${recordId}/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },
};
