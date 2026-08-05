import apiClient from './apiClient'

export type NotificationType = 'info' | 'success' | 'warning' | 'error' | 'work_order' | 'inventory' | 'maintenance' | 'quality'

export interface Notification {
  id: number
  type: NotificationType
  title: string
  message: string
  link?: string
  read: boolean
  created_at: string
}

export interface NotificationFilters {
  page?: number
  limit?: number
  unread_only?: boolean
  type?: NotificationType
}

class NotificationService {
  private baseUrl = '/api/v1/notifications'

  // Mock implementation - replace with real API calls when backend is ready
  async getNotifications(filters: NotificationFilters = {}): Promise<{
    data: Notification[]
    total: number
    unread_count: number
  }> {
    const mockNotifications: Notification[] = []

    const filteredNotifications = filters.unread_only
      ? mockNotifications.filter((n) => !n.read)
      : mockNotifications

    return {
      data: filteredNotifications,
      total: filteredNotifications.length,
      unread_count: mockNotifications.filter((n) => !n.read).length,
    }
  }

  async markAsRead(id: number): Promise<void> {
    // Mock implementation
    return Promise.resolve()
  }

  async markAllAsRead(): Promise<void> {
    // Mock implementation
    return Promise.resolve()
  }

  async deleteNotification(id: number): Promise<void> {
    // Mock implementation
    return Promise.resolve()
  }
}

export const notificationService = new NotificationService()
