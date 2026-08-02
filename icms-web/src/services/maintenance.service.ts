import apiClient from './apiClient'

export interface MaintenanceReport {
  id: number
  report_number: string
  work_order_id: number
  equipment_id: number
  craftsman_id: number
  work_performed: string
  findings?: string
  recommendations?: string
  parts_used?: string
  labor_hours?: number
  equipment_operational: boolean
  follow_up_required: boolean
  attachments?: string
  completed_at?: string
  reviewed_by?: number
  reviewed_at?: string
  created_at: string
  updated_at: string
  // Extended fields
  equipment_name?: string
  craftsman_name?: string
  work_order_number?: string
  reviewer_name?: string
}

export interface CreateMaintenanceReportRequest {
  work_order_id: number
  equipment_id: number
  craftsman_id: number
  work_performed: string
  findings?: string
  recommendations?: string
  parts_used?: string
  labor_hours?: number
  equipment_operational?: boolean
  follow_up_required?: boolean
}

export interface UpdateMaintenanceReportRequest {
  work_performed?: string
  findings?: string
  recommendations?: string
  parts_used?: string
  labor_hours?: number
  equipment_operational?: boolean
  follow_up_required?: boolean
  attachments?: string
}

export interface MaintenanceFilters {
  page?: number
  limit?: number
  search?: string
  equipment_id?: number
  craftsman_id?: number
}

export interface MaintenanceStatistics {
  total_reports: number
  reviewed_count: number
  pending_review: number
  follow_up_required: number
  equipment_operational: number
  total_labor_hours: number
}

class MaintenanceService {
  private baseUrl = '/api/v1/maintenance'

  async getAll(filters: MaintenanceFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.equipment_id) params.append('equipment_id', filters.equipment_id.toString())
    if (filters.craftsman_id) params.append('craftsman_id', filters.craftsman_id.toString())

    const url = `${this.baseUrl}/reports?${params.toString()}`
    return apiClient.get<{
      success: boolean
      data: MaintenanceReport[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(url)
  }

  async getStatistics() {
    return apiClient.get<MaintenanceStatistics>(`${this.baseUrl}/statistics`)
  }

  async getById(id: number) {
    return apiClient.get<MaintenanceReport>(`${this.baseUrl}/reports/${id}`)
  }

  async create(data: CreateMaintenanceReportRequest) {
    return apiClient.post<MaintenanceReport>(`${this.baseUrl}/reports`, data)
  }

  async update(id: number, data: UpdateMaintenanceReportRequest) {
    return apiClient.put<MaintenanceReport>(`${this.baseUrl}/reports/${id}`, data)
  }

  async delete(id: number) {
    return apiClient.delete(`${this.baseUrl}/reports/${id}`)
  }

  async review(id: number) {
    return apiClient.post<MaintenanceReport>(`${this.baseUrl}/reports/${id}/review`, {})
  }

  async getByWorkOrder(workOrderId: number) {
    return apiClient.get<MaintenanceReport[]>(
      `${this.baseUrl}/reports/by-work-order/${workOrderId}`
    )
  }

  async getByEquipment(equipmentId: number) {
    return apiClient.get<MaintenanceReport[]>(
      `${this.baseUrl}/reports/by-equipment/${equipmentId}`
    )
  }

  async getByCraftsman(craftsmanId: number) {
    return apiClient.get<MaintenanceReport[]>(
      `${this.baseUrl}/reports/by-craftsman/${craftsmanId}`
    )
  }
}

export const maintenanceService = new MaintenanceService()
