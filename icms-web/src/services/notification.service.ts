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

  async getNotifications(filters: NotificationFilters = {}): Promise<{
    data: Notification[]
    total: number
    unread_count: number
  }> {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.unread_only) params.append('unread_only', 'true')
    if (filters.type) params.append('type', filters.type)
    return apiClient.get(`${this.baseUrl}?${params.toString()}`)
  }

  async markAsRead(id: number): Promise<void> {
    await apiClient.post(`${this.baseUrl}/${id}/read`)
  }

  async markAllAsRead(): Promise<void> {
    await apiClient.post(`${this.baseUrl}/read-all`)
  }

  async deleteNotification(id: number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`)
  }
}

export const notificationService = new NotificationService()
