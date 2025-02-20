/**
 * Hook for managing notifications.
 */
import { useState, useEffect, useCallback } from 'react';
import { useApi } from './useApi';
import notificationService, { Notification } from '../api/services/notifications';

interface UseNotificationsOptions {
  pollingInterval?: number;
  unreadOnly?: boolean;
  limit?: number;
}

export function useNotifications({
  pollingInterval = 30000,  // 30 seconds
  unreadOnly = false,
  limit = 50
}: UseNotificationsOptions = {}) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const {
    data,
    loading,
    error,
    execute: fetchNotifications
  } = useApi(() => notificationService.getNotifications(unreadOnly, limit));

  // Update notifications and unread count
  useEffect(() => {
    if (data) {
      setNotifications(data);
      setUnreadCount(data.filter(n => !n.read).length);
    }
  }, [data]);

  // Poll for new notifications
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, pollingInterval);
    return () => clearInterval(interval);
  }, [fetchNotifications, pollingInterval]);

  // Mark a notification as read
  const markAsRead = useCallback(async (id: number) => {
    try {
      const updated = await notificationService.markAsRead(id);
      setNotifications(current =>
        current.map(n => (n.id === id ? { ...n, read: true } : n))
      );
      setUnreadCount(current => current - 1);
      return updated;
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      throw error;
    }
  }, []);

  // Mark all notifications as read
  const markAllAsRead = useCallback(async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications(current =>
        current.map(n => ({ ...n, read: true }))
      );
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
      throw error;
    }
  }, []);

  // Add a new notification
  const addNotification = useCallback((notification: Notification) => {
    setNotifications(current => [notification, ...current]);
    if (!notification.read) {
      setUnreadCount(current => current + 1);
    }
  }, []);

  // Remove a notification
  const removeNotification = useCallback((id: number) => {
    setNotifications(current => {
      const notification = current.find(n => n.id === id);
      if (notification && !notification.read) {
        setUnreadCount(count => count - 1);
      }
      return current.filter(n => n.id !== id);
    });
  }, []);

  return {
    notifications,
    unreadCount,
    loading,
    error,
    markAsRead,
    markAllAsRead,
    addNotification,
    removeNotification,
    refresh: fetchNotifications
  };
}

export default useNotifications;