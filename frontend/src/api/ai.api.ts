import { apiClient } from './axios';
import type { AnalyzeRequest, AnalyzeResponse, AnalysisResult } from '../types';

export const aiApi = {
  analyze: (data: AnalyzeRequest) =>
    apiClient.post<AnalyzeResponse>('/ai/analyze', data).then((r) => r.data),

  results: (analysisId: string) =>
    apiClient.get<AnalysisResult>(`/ai/results/${analysisId}`).then((r) => r.data),
};
