/**
 * Notifications API service.
 */
import apiClient from '../client';

export interface Notification {
  id: number;
  user_id: number;
  type: string;
  title: string;
  content: string;
  read: boolean;
  created_at: string;
  delivered_at?: string;
}

export interface NotificationCreate {
  user_id: number;
  type: string;
  title: string;
  content: string;
}

class NotificationService {
  async getNotifications(unreadOnly = false, limit = 50): Promise<Notification[]> {
    return apiClient.get<Notification[]>('/api/notifications', {
      unread_only: unreadOnly,
      limit
    });
  }

  async createNotification(data: NotificationCreate): Promise<Notification> {
    return apiClient.post<Notification>('/api/notifications', data);
  }

  async markAsRead(id: number): Promise<Notification> {
    return apiClient.post<Notification>(`/api/notifications/${id}/read`);
  }

  async markAllAsRead(): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>('/api/notifications/mark-all-read');
  }

  async cleanupNotifications(days = 30): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>('/api/notifications/cleanup', {
      params: { days }
    });
  }
}

export const notificationService = new NotificationService();
export default notificationService;