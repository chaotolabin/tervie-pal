import apiClient from './apiClient';

export const AdminService = {
  // Dashboard
  getDashboard: async () => {
    const response = await apiClient.get('/admin/dashboard');
    return response.data;
  },

  getDashboardStats: async (range: '7d' | '30d' | '90d' = '7d', topN: number = 10) => {
    const response = await apiClient.get('/admin/dashboard/stats', {
      params: { range, top_n: topN }
    });
    return response.data;
  },

  getDailyStats: async (days: number = 30) => {
    const response = await apiClient.get('/admin/dashboard/daily-stats', {
      params: { days }
    });
    return response.data;
  },

  getCoreDashboard: async (range: '7d' | '30d' | '90d' = '7d') => {
    const response = await apiClient.get('/admin/dashboard/core', {
      params: { range }
    });
    return response.data;
  },

  getBlogDashboard: async (range: '7d' | '30d' | '90d' = '7d', topN: number = 10) => {
    const response = await apiClient.get('/admin/dashboard/blog', {
      params: { range, top_n: topN }
    });
    return response.data;
  },

  getStreakDashboard: async (range: '7d' | '30d' | '90d' = '7d', topN: number = 10) => {
    const response = await apiClient.get('/admin/dashboard/streak', {
      params: { range, top_n: topN }
    });
    return response.data;
  },

  // Users
  getUsers: async (params?: {
    page?: number;
    page_size?: number;
    email?: string;
    role?: 'user' | 'admin';
  }) => {
    const response = await apiClient.get('/admin/users', { params });
    return response.data;
  },

  getUserDetail: async (userId: string) => {
    const response = await apiClient.get(`/admin/users/${userId}`);
    return response.data;
  },

  updateUserRole: async (userId: string, role: 'user' | 'admin') => {
    const response = await apiClient.patch(`/admin/users/${userId}/role`, { role });
    return response.data;
  },

  adjustUserStreak: async (userId: string, currentStreak: number, reason: string) => {
    const response = await apiClient.post(`/admin/users/${userId}/streak/adjust`, {
      current_streak: currentStreak,
      reason
    });
    return response.data;
  },

  // Support
  getAllTickets: async (params?: {
    status?: 'open' | 'in_progress' | 'resolved' | 'closed';
    category?: 'bug' | 'feature_request' | 'question' | 'other';
    limit?: number;
    cursor?: string;
  }) => {
    const response = await apiClient.get('/admin/support/tickets', { params });
    return response.data;
  },

  updateTicket: async (ticketId: number, data: {
    status?: 'open' | 'in_progress' | 'resolved' | 'closed';
    category?: 'bug' | 'feature_request' | 'question' | 'other';
  }) => {
    const response = await apiClient.patch(`/admin/support/tickets/${ticketId}`, data);
    return response.data;
  },

  // Blog
  getPosts: async (params?: {
    page?: number;
    page_size?: number;
    include_deleted?: boolean;
  }) => {
    const response = await apiClient.get('/admin/posts', { params });
    return response.data;
  },

  deletePost: async (postId: number, reason?: string) => {
    const response = await apiClient.delete(`/admin/posts/${postId}`, {
      data: reason ? { reason } : undefined
    });
    return response.data;
  },

  restorePost: async (postId: number) => {
    const response = await apiClient.post(`/admin/posts/${postId}/restore`);
    return response.data;
  }
};

