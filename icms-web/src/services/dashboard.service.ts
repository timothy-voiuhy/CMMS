import apiClient from './apiClient'
import type { InventoryItem } from './inventory.service'

export interface DashboardStats {
  equipment: {
    total: number
    operational: number
    maintenance_due: number
    out_of_service: number
  }
  craftsmen: {
    total: number
    active: number
    available: number
  }
  inventory: {
    total_items: number
    low_stock_count: number
    out_of_stock_count: number
    total_value: number
  }
  workOrders: {
    total: number
    open: number
    in_progress: number
    completed: number
    cancelled: number
  }
}

export interface WorkOrderSummary {
  id: number
  order_number: string
  title: string
  description?: string
  status: string
  priority: string
  created_at: string
}

class DashboardService {
  async getEquipmentStats() {
    return apiClient.get<DashboardStats['equipment']>('/api/v1/equipment/statistics')
  }

  async getCraftsmenStats() {
    return apiClient.get<DashboardStats['craftsmen']>('/api/v1/craftsmen/statistics')
  }

  async getInventoryStats() {
    return apiClient.get<DashboardStats['inventory']>('/api/v1/inventory/statistics')
  }

  async getWorkOrderStats() {
    return apiClient.get<DashboardStats['workOrders']>('/api/v1/work-orders/statistics')
  }

  async getAllStats(): Promise<DashboardStats> {
    const [equipment, craftsmen, inventory, workOrders] = await Promise.all([
      this.getEquipmentStats(),
      this.getCraftsmenStats(),
      this.getInventoryStats(),
      this.getWorkOrderStats(),
    ])

    return {
      equipment,
      craftsmen,
      inventory,
      workOrders,
    }
  }

  async getRecentWorkOrders(limit: number = 5) {
    const response = await apiClient.get<{
      success: boolean
      data: WorkOrderSummary[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(`/api/v1/work-orders/?page=1&limit=${limit}`)
    return response.data
  }

  async getLowStockItems(limit: number = 10) {
    return apiClient.get<InventoryItem[]>('/api/v1/inventory/low-stock')
  }
}

export const dashboardService = new DashboardService()
