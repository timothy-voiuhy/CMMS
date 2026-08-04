import { apiClient } from './apiClient'
import type { Craftsman, PaginatedResponse } from '../types'

export interface CreateCraftsmanRequest {
  user_id: number
  employee_id: string
  department?: string
  position?: string
  role_id?: number
  hire_date?: string
  certification_level?: string
  hourly_rate?: number
  notes?: string
}

export interface UpdateCraftsmanRequest extends Partial<CreateCraftsmanRequest> {}

export interface CraftsmanFilters {
  department?: string
  position?: string
  certification_level?: string
  search?: string
  page?: number
  limit?: number
}

export interface CraftsmanSkill {
  id: number
  name: string
  description?: string
  category?: string
}

export interface CraftsmanWithUser extends Craftsman {
  username: string
  email: string
  full_name: string
  phone?: string
  user?: {
    id: number
    username: string
    email: string
    full_name: string
    phone?: string
    is_active: boolean
  }
  skills?: CraftsmanSkill[]
}

export const craftsmanService = {
  /**
   * Get all craftsmen with optional filters
   */
  async getAll(filters?: CraftsmanFilters): Promise<PaginatedResponse<CraftsmanWithUser>> {
    const params = new URLSearchParams()
    
    if (filters?.department) params.append('department', filters.department)
    if (filters?.position) params.append('position', filters.position)
    if (filters?.certification_level) params.append('certification_level', filters.certification_level)
    if (filters?.search) params.append('search', filters.search)
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())

    return apiClient.get<PaginatedResponse<CraftsmanWithUser>>(
      `/api/v1/craftsmen/?${params.toString()}`
    )
  },

  /**
   * Get craftsman by ID
   */
  async getById(id: number): Promise<CraftsmanWithUser> {
    return apiClient.get<CraftsmanWithUser>(`/api/v1/craftsmen/${id}`)
  },

  /**
   * Create new craftsman
   */
  async create(data: CreateCraftsmanRequest): Promise<CraftsmanWithUser> {
    return apiClient.post<CraftsmanWithUser>('/api/v1/craftsmen/', data)
  },

  /**
   * Update craftsman
   */
  async update(id: number, data: UpdateCraftsmanRequest): Promise<CraftsmanWithUser> {
    return apiClient.put<CraftsmanWithUser>(`/api/v1/craftsmen/${id}`, data)
  },

  /**
   * Delete craftsman
   */
  async delete(id: number): Promise<void> {
    return apiClient.delete(`/api/v1/craftsmen/${id}`)
  },

  /**
   * Get craftsman skills
   */
  async getSkills(craftsmanId: number): Promise<CraftsmanSkill[]> {
    return apiClient.get<CraftsmanSkill[]>(`/api/v1/craftsmen/${craftsmanId}/skills`)
  },

  /**
   * Add skill to craftsman
   */
  async addSkill(craftsmanId: number, skillId: number): Promise<void> {
    return apiClient.post(`/api/v1/craftsmen/${craftsmanId}/skills/${skillId}`)
  },

  /**
   * Remove skill from craftsman
   */
  async removeSkill(craftsmanId: number, skillId: number): Promise<void> {
    return apiClient.delete(`/api/v1/craftsmen/${craftsmanId}/skills/${skillId}`)
  },

  /**
   * Get equipment operated by craftsman
   */
  async getOperatedEquipment(craftsmanId: number): Promise<any[]> {
    return apiClient.get(`/api/v1/craftsmen/${craftsmanId}/equipment`)
  },

  /**
   * Get work orders assigned to craftsman
   */
  async getWorkOrders(craftsmanId: number): Promise<any[]> {
    return apiClient.get(`/api/v1/craftsmen/${craftsmanId}/work-orders`)
  },

  /**
   * Get overall craftsmen statistics
   */
  async getOverallStatistics(): Promise<{
    total: number
    active: number
    inactive: number
    byDepartment: Record<string, number>
  }> {
    return apiClient.get('/api/v1/craftsmen/statistics')
  },

  /**
   * Get individual craftsman statistics
   */
  async getStatistics(craftsmanId: number): Promise<{
    totalWorkOrders: number
    completedWorkOrders: number
    pendingWorkOrders: number
    averageCompletionTime: number
  }> {
    return apiClient.get(`/api/v1/craftsmen/${craftsmanId}/statistics`)
  },
}

export default craftsmanService
