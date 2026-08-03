import apiClient from './apiClient'

// ==================== TYPES ====================

export type InspectionStatus = 'pending' | 'in_progress' | 'completed' | 'failed'
export type InspectionResult = 'pass' | 'fail' | 'conditional' | 'pending'
export type NCRStatus = 'open' | 'investigating' | 'corrective_action' | 'closed' | 'rejected'
export type NCRSeverity = 'critical' | 'major' | 'minor'

export interface QualityInspectionItem {
  id?: number
  inspection_id?: number
  checkpoint_name: string
  specification?: string
  measured_value?: string
  result: InspectionResult
  notes?: string
  created_at?: string
}

export interface QualityInspection {
  id: number
  inspection_number: string
  production_order_id?: number
  batch_number?: string
  product_name: string
  inspection_type: string
  inspection_date: string
  inspector_id: number
  sample_size?: number
  defects_found: number
  specifications?: string
  status: InspectionStatus
  result: InspectionResult
  pass_rate?: number
  observations?: string
  notes?: string
  created_at: string
  updated_at: string
  completed_at?: string
  inspection_items: QualityInspectionItem[]
}

export interface NonConformanceReport {
  id: number
  ncr_number: string
  inspection_id?: number
  production_order_id?: number
  equipment_id?: number
  batch_number?: string
  title: string
  description: string
  severity: NCRSeverity
  status: NCRStatus
  reported_by_id: number
  assigned_to_id?: number
  root_cause?: string
  corrective_action?: string
  preventive_action?: string
  estimated_cost?: number
  created_at: string
  updated_at: string
  closed_at?: string
}

export interface CreateInspectionRequest {
  production_order_id?: number
  batch_number?: string
  product_name: string
  inspection_type: string
  inspection_date: string
  inspector_id: number
  sample_size?: number
  specifications?: string
  observations?: string
  notes?: string
  inspection_items: Omit<QualityInspectionItem, 'id' | 'inspection_id' | 'created_at'>[]
}

export interface UpdateInspectionRequest {
  production_order_id?: number
  batch_number?: string
  product_name?: string
  inspection_type?: string
  inspection_date?: string
  sample_size?: number
  defects_found?: number
  specifications?: string
  status?: InspectionStatus
  result?: InspectionResult
  pass_rate?: number
  observations?: string
  notes?: string
}

export interface CreateNCRRequest {
  inspection_id?: number
  production_order_id?: number
  equipment_id?: number
  batch_number?: string
  title: string
  description: string
  severity: NCRSeverity
  reported_by_id: number
  assigned_to_id?: number
  root_cause?: string
  corrective_action?: string
  preventive_action?: string
  estimated_cost?: number
}

export interface UpdateNCRRequest {
  inspection_id?: number
  production_order_id?: number
  equipment_id?: number
  batch_number?: string
  title?: string
  description?: string
  severity?: NCRSeverity
  status?: NCRStatus
  assigned_to_id?: number
  root_cause?: string
  corrective_action?: string
  preventive_action?: string
  estimated_cost?: number
}

export interface QualityStatistics {
  total_inspections: number
  pending_inspections: number
  completed_inspections: number
  pass_rate: number
  fail_rate: number
  total_ncrs: number
  open_ncrs: number
  critical_ncrs: number
  avg_defects_per_inspection: number
}

export interface InspectionFilters {
  page?: number
  limit?: number
  status?: InspectionStatus
  result?: InspectionResult
  search?: string
}

export interface NCRFilters {
  page?: number
  limit?: number
  status?: NCRStatus
  severity?: NCRSeverity
  search?: string
}

// ==================== SERVICE ====================

class QualityService {
  private baseUrl = '/api/v1/quality'

  // Statistics
  async getStatistics() {
    return apiClient.get<QualityStatistics>(`${this.baseUrl}/statistics`)
  }

  // Inspections
  async getInspections(filters: InspectionFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.status) params.append('status', filters.status)
    if (filters.result) params.append('result', filters.result)
    if (filters.search) params.append('search', filters.search)

    return apiClient.get<{
      success: boolean
      data: QualityInspection[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(`${this.baseUrl}/inspections?${params.toString()}`)
  }

  async getInspectionById(id: number) {
    return apiClient.get<QualityInspection>(`${this.baseUrl}/inspections/${id}`)
  }

  async createInspection(data: CreateInspectionRequest) {
    return apiClient.post<QualityInspection>(`${this.baseUrl}/inspections`, data)
  }

  async updateInspection(id: number, data: UpdateInspectionRequest) {
    return apiClient.put<QualityInspection>(`${this.baseUrl}/inspections/${id}`, data)
  }

  async deleteInspection(id: number) {
    return apiClient.delete(`${this.baseUrl}/inspections/${id}`)
  }

  // NCRs
  async getNCRs(filters: NCRFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.status) params.append('status', filters.status)
    if (filters.severity) params.append('severity', filters.severity)
    if (filters.search) params.append('search', filters.search)

    return apiClient.get<{
      success: boolean
      data: NonConformanceReport[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(`${this.baseUrl}/ncrs?${params.toString()}`)
  }

  async getNCRById(id: number) {
    return apiClient.get<NonConformanceReport>(`${this.baseUrl}/ncrs/${id}`)
  }

  async createNCR(data: CreateNCRRequest) {
    return apiClient.post<NonConformanceReport>(`${this.baseUrl}/ncrs`, data)
  }

  async updateNCR(id: number, data: UpdateNCRRequest) {
    return apiClient.put<NonConformanceReport>(`${this.baseUrl}/ncrs/${id}`, data)
  }

  async deleteNCR(id: number) {
    return apiClient.delete(`${this.baseUrl}/ncrs/${id}`)
  }
}

export const qualityService = new QualityService()
