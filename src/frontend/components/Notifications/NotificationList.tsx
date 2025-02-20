/**
 * Notification list component.
 */
import React from 'react';
import { Bell, X } from 'lucide-react';
import useNotifications from '../../hooks/useNotifications';

export function NotificationList() {
  const {
    notifications,
    unreadCount,
    loading,
    markAsRead,
    markAllAsRead
  } = useNotifications();

  if (loading) {
    return (
      <div className="p-4 text-center">
        <span className="text-gray-500">Loading notifications...</span>
      </div>
    );
  }

  if (!notifications.length) {
    return (
      <div className="p-4 text-center">
        <Bell className="mx-auto h-8 w-8 text-gray-400" />
        <p className="mt-2 text-gray-500">No notifications</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {unreadCount > 0 && (
        <div className="flex items-center justify-between p-2 bg-gray-50 border-b">
          <span className="text-sm text-gray-600">
            {unreadCount} unread {unreadCount === 1 ? 'notification' : 'notifications'}
          </span>
          <button
            onClick={() => markAllAsRead()}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Mark all as read
          </button>
        </div>
      )}

      <div className="max-h-96 overflow-y-auto">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`
              p-4 border-b last:border-b-0 hover:bg-gray-50 transition-colors
              ${notification.read ? 'bg-white' : 'bg-blue-50'}
            `}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className={`
                  text-sm font-medium
                  ${notification.read ? 'text-gray-900' : 'text-blue-900'}
                `}>
                  {notification.title}
                </h4>
                <p className="mt-1 text-sm text-gray-600">
                  {notification.content}
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  {new Date(notification.created_at).toLocaleDateString()}
                </p>
              </div>

              {!notification.read && (
                <button
                  onClick={() => markAsRead(notification.id)}
                  className="ml-4 text-gray-400 hover:text-gray-600"
                  title="Mark as read"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default NotificationList;