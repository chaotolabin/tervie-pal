import apiClient from './apiClient';

export interface SupportTicketCreateRequest {
  subject: string;
  message: string;
  category?: 'bug' | 'feature_request' | 'question' | 'other';
}

export interface SupportTicketResponse {
  id: number;
  subject: string;
  message: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  category: 'bug' | 'feature_request' | 'question' | 'other';
  created_at: string;
  updated_at: string;
}

export interface SupportTicketListResponse {
  items: SupportTicketResponse[];
  next_cursor?: string;
}

export const SupportService = {
  createTicket: async (data: SupportTicketCreateRequest): Promise<SupportTicketResponse> => {
    const response = await apiClient.post('/support/tickets', data);
    return response.data;
  },

  getMyTickets: async (params?: {
    status?: 'open' | 'in_progress' | 'resolved' | 'closed';
    category?: 'bug' | 'feature_request' | 'question' | 'other';
    limit?: number;
    cursor?: string;
  }): Promise<SupportTicketListResponse> => {
    const response = await apiClient.get('/support/tickets', { params });
    return response.data;
  }
};

