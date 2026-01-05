import apiClient from './apiClient';

export interface CreateNotificationRequest {
  user_id: string;
  title: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  link?: string;
}

export const NotificationService = {
  create: async (data: CreateNotificationRequest) => {
    const response = await apiClient.post('/notifications', data);
    return response.data;
  },

  getMyNotifications: async (params?: {
    limit?: number;
    cursor?: string;
    unread_only?: boolean;
  }) => {
    const response = await apiClient.get('/notifications', { params });
    return response.data;
  },

  markAsRead: async (notificationId: number) => {
    const response = await apiClient.patch(`/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await apiClient.patch('/notifications/read-all');
    return response.data;
  }
};

