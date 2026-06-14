import { apiClient } from './axios';
import type { ChatQuery, ChatResponse } from '../types';

export const chatApi = {
  query: (payload: ChatQuery) =>
    apiClient.post<ChatResponse>('/chat/query', payload).then((r) => r.data),
};
