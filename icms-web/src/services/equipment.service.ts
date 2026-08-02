import { apiClient } from './apiClient'
import type { Equipment, PaginatedResponse } from '../types'

export interface EquipmentStatus {
  OPERATIONAL: string
  MAINTENANCE: string
  BREAKDOWN: string
  RETIRED: string
}

export interface CreateEquipmentRequest {
  name: string
  equipment_id: string
  category?: string
  manufacturer?: string
  model?: string
  serial_number?: string
  location?: string
  status?: string
  purchase_date?: string
  warranty_expiry?: string
  specifications?: string
  notes?: string
  parent_id?: number
}

export interface UpdateEquipmentRequest extends Partial<CreateEquipmentRequest> {}

export interface EquipmentFilters {
  category?: string
  status?: string
  location?: string
  search?: string
  page?: number
  limit?: number
}

export interface EquipmentOperator {
  craftsman_id: number
  craftsman_name: string
  employee_id: string
}

export const equipmentService = {
  /**
   * Get all equipment with optional filters
   */
  async getAll(filters?: EquipmentFilters): Promise<PaginatedResponse<Equipment>> {
    const params = new URLSearchParams()
    
    if (filters?.category) params.append('category', filters.category)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.location) params.append('location', filters.location)
    if (filters?.search) params.append('search', filters.search)
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())

    return apiClient.get<PaginatedResponse<Equipment>>(
      `/api/v1/equipment/?${params.toString()}`
    )
  },

  /**
   * Get equipment by ID
   */
  async getById(id: number): Promise<Equipment> {
    return apiClient.get<Equipment>(`/api/v1/equipment/${id}`)
  },

  /**
   * Create new equipment
   */
  async create(data: CreateEquipmentRequest): Promise<Equipment> {
    return apiClient.post<Equipment>('/api/v1/equipment/', data)
  },

  /**
   * Update equipment
   */
  async update(id: number, data: UpdateEquipmentRequest): Promise<Equipment> {
    return apiClient.put<Equipment>(`/api/v1/equipment/${id}`, data)
  },

  /**
   * Delete equipment
   */
  async delete(id: number): Promise<void> {
    return apiClient.delete(`/api/v1/equipment/${id}`)
  },

  /**
   * Get equipment operators
   */
  async getOperators(equipmentId: number): Promise<EquipmentOperator[]> {
    return apiClient.get<EquipmentOperator[]>(`/api/v1/equipment/${equipmentId}/operators`)
  },

  /**
   * Assign operator to equipment
   */
  async assignOperator(equipmentId: number, craftsmanId: number): Promise<void> {
    return apiClient.post(`/api/v1/equipment/${equipmentId}/operators/${craftsmanId}`)
  },

  /**
   * Remove operator from equipment
   */
  async removeOperator(equipmentId: number, craftsmanId: number): Promise<void> {
    return apiClient.delete(`/api/v1/equipment/${equipmentId}/operators/${craftsmanId}`)
  },

  /**
   * Get equipment statistics
   */
  async getStatistics(): Promise<{
    total: number
    operational: number
    maintenance: number
    breakdown: number
    retired: number
  }> {
    return apiClient.get('/api/v1/equipment/statistics')
  },

  /**
   * Export equipment to CSV
   */
  async exportToCSV(filters?: EquipmentFilters): Promise<void> {
    const params = new URLSearchParams()
    
    if (filters?.category) params.append('category', filters.category)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.location) params.append('location', filters.location)

    return apiClient.download(
      `/api/v1/equipment/export?${params.toString()}`,
      'equipment-export.csv'
    )
  },
}

export default equipmentService
