import { apiClient } from './axios';
import type { AnalyzeRequest, AnalyzeResponse, AnalysisResult, DiagnosisResult } from '../types';

export const aiApi = {
  /**
   * Run the LVLM diagnostic pipeline on an uploaded image / lab PDF.
   * Returns draft -> recheck -> final diagnosis (always doctor-review-gated).
   */
  diagnose: (file: File, modality?: string) => {
    const form = new FormData();
    form.append('file', file);
    if (modality) form.append('modality', modality);
    return apiClient
      .post<DiagnosisResult>('/ai/diagnose', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },

  analyze: (data: AnalyzeRequest) =>
    apiClient.post<AnalyzeResponse>('/ai/analyze', data).then((r) => r.data),

  results: (analysisId: string) =>
    apiClient.get<AnalysisResult>(`/ai/results/${analysisId}`).then((r) => r.data),
};
