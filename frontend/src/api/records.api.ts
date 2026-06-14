import { apiClient } from './axios';
import type { MedicalRecord, MessageResponse } from '../types';

export const recordsApi = {
  create: (record: Partial<MedicalRecord>) =>
    apiClient.post<MessageResponse>('/medical/records', record).then((r) => r.data),

  getById: (id: number) =>
    apiClient.get(`/medical/records/${id}`).then((r) => r.data),

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
