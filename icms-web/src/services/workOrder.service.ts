import apiClient from './apiClient'

export type WorkOrderType =
  | 'preventive'
  | 'corrective'
  | 'predictive'
  | 'emergency'
  | 'modification'
  | 'inspection'

export type WorkOrderPriority = 'low' | 'medium' | 'high' | 'urgent'

export type WorkOrderStatus =
  | 'pending'
  | 'assigned'
  | 'in_progress'
  | 'on_hold'
  | 'completed'
  | 'cancelled'

export interface WorkOrder {
  id: number
  work_order_number: string
  title: string
  description?: string
  work_order_type: WorkOrderType
  priority: WorkOrderPriority
  status: WorkOrderStatus
  equipment_id?: number
  assigned_to?: number
  created_by: number
  scheduled_date?: string
  due_date?: string
  started_at?: string
  completed_at?: string
  estimated_hours?: number
  actual_hours?: number
  notes?: string
  completion_notes?: string
  created_at: string
  updated_at: string
}

export interface CreateWorkOrderRequest {
  title: string
  description?: string
  work_order_type: WorkOrderType
  priority?: WorkOrderPriority
  equipment_id?: number
  scheduled_date?: string
  due_date?: string
  estimated_hours?: number
  notes?: string
}

export interface UpdateWorkOrderRequest {
  title?: string
  description?: string
  priority?: WorkOrderPriority
  status?: WorkOrderStatus
  assigned_to?: number
  scheduled_date?: string
  due_date?: string
  estimated_hours?: number
  actual_hours?: number
  notes?: string
  completion_notes?: string
}

export interface WorkOrderFilters {
  page?: number
  limit?: number
  search?: string
  status?: WorkOrderStatus
  priority?: WorkOrderPriority
  assigned_to?: number
}

export interface WorkOrderStatistics {
  total: number
  pending: number
  assigned: number
  in_progress: number
  completed: number
  on_hold: number
  urgent: number
}

class WorkOrderService {
  private baseUrl = '/api/v1/work-orders'

  async getAll(filters: WorkOrderFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.status) params.append('status', filters.status)
    if (filters.priority) params.append('priority', filters.priority)
    if (filters.assigned_to) params.append('assigned_to', filters.assigned_to.toString())

    const url = `${this.baseUrl}/?${params.toString()}`
    return apiClient.get<{
      success: boolean
      data: WorkOrder[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(url)
  }

  async getStatistics() {
    return apiClient.get<WorkOrderStatistics>(`${this.baseUrl}/statistics`)
  }

  async getById(id: number) {
    return apiClient.get<WorkOrder>(`${this.baseUrl}/${id}`)
  }

  async create(data: CreateWorkOrderRequest) {
    return apiClient.post<WorkOrder>(this.baseUrl, data)
  }

  async update(id: number, data: UpdateWorkOrderRequest) {
    return apiClient.put<WorkOrder>(`${this.baseUrl}/${id}`, data)
  }

  async delete(id: number) {
    return apiClient.delete(`${this.baseUrl}/${id}`)
  }

  async assign(id: number, craftsmanId: number) {
    return apiClient.post<WorkOrder>(`${this.baseUrl}/${id}/assign`, {
      craftsman_id: craftsmanId,
    })
  }

  async updateStatus(id: number, status: WorkOrderStatus, notes?: string) {
    return apiClient.patch<WorkOrder>(`${this.baseUrl}/${id}/status`, {
      status,
      notes,
    })
  }

  async getByCraftsman(craftsmanId: number) {
    return apiClient.get<WorkOrder[]>(`${this.baseUrl}/by-craftsman/${craftsmanId}`)
  }

  async getByEquipment(equipmentId: number) {
    return apiClient.get<WorkOrder[]>(`${this.baseUrl}/by-equipment/${equipmentId}`)
  }
}

export const workOrderService = new WorkOrderService()
