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

export type MaintenanceCatalogueItemType = 'spare_part' | 'tool'

export interface MaintenanceCatalogueItem {
  id: number
  item_code: string
  item_type: MaintenanceCatalogueItemType
  name: string
  description?: string
  category?: string
  image_url?: string
  manufacturer?: string
  model_number?: string
  supplier?: string
  unit_of_measure?: string
  unit_cost?: number
  location?: string
  compatible_equipment?: string
  inventory_item_id?: number
  is_active: boolean
  notes?: string
  created_at: string
  updated_at: string
}

export interface CreateMaintenanceCatalogueItemRequest {
  item_code?: string
  item_type: MaintenanceCatalogueItemType
  name: string
  description?: string
  category?: string
  image_url?: string
  manufacturer?: string
  model_number?: string
  supplier?: string
  unit_of_measure?: string
  unit_cost?: number
  location?: string
  compatible_equipment?: string
  inventory_item_id?: number
  is_active?: boolean
  notes?: string
}

export type UpdateMaintenanceCatalogueItemRequest = Partial<CreateMaintenanceCatalogueItemRequest>

export interface MaintenanceCatalogueFilters {
  page?: number
  limit?: number
  search?: string
  category?: string
  item_type?: MaintenanceCatalogueItemType
  include_inactive?: boolean
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

  async getCatalogue(filters: MaintenanceCatalogueFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.category) params.append('category', filters.category)
    if (filters.item_type) params.append('item_type', filters.item_type)
    if (filters.include_inactive) params.append('include_inactive', 'true')

    return apiClient.get<{
      success: boolean
      data: MaintenanceCatalogueItem[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(`${this.baseUrl}/catalogue?${params.toString()}`)
  }

  async getCatalogueCategories() {
    return apiClient.get<string[]>(`${this.baseUrl}/catalogue/categories`)
  }

  async getCatalogueItemById(id: number) {
    return apiClient.get<MaintenanceCatalogueItem>(`${this.baseUrl}/catalogue/${id}`)
  }

  async createCatalogueItem(data: CreateMaintenanceCatalogueItemRequest) {
    return apiClient.post<MaintenanceCatalogueItem>(`${this.baseUrl}/catalogue`, data)
  }

  async updateCatalogueItem(id: number, data: UpdateMaintenanceCatalogueItemRequest) {
    return apiClient.put<MaintenanceCatalogueItem>(`${this.baseUrl}/catalogue/${id}`, data)
  }

  async deleteCatalogueItem(id: number) {
    return apiClient.delete(`${this.baseUrl}/catalogue/${id}`)
  }
}

export const maintenanceService = new MaintenanceService()
