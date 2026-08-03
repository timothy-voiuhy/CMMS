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
    // Mock data for now
    const mockNotifications: Notification[] = [
      {
        id: 1,
        type: 'work_order',
        title: 'New work order assigned',
        message: 'WO-2024-001 requires your attention',
        link: '/work-orders/1',
        read: false,
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 2,
        type: 'inventory',
        title: 'Low stock alert',
        message: 'Item BRG-001 is below reorder point',
        link: '/inventory/1',
        read: false,
        created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 3,
        type: 'maintenance',
        title: 'Maintenance due',
        message: 'Equipment EQ-125 scheduled maintenance tomorrow',
        link: '/maintenance/reports/1',
        read: true,
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 4,
        type: 'quality',
        title: 'Quality inspection completed',
        message: 'Batch QI-2024-045 passed inspection',
        link: '/quality',
        read: true,
        created_at: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 5,
        type: 'success',
        title: 'Production order completed',
        message: 'PO-2024-123 has been completed successfully',
        link: '/production',
        read: true,
        created_at: new Date(Date.now() - 72 * 60 * 60 * 1000).toISOString(),
      },
    ]

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
