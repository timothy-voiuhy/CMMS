import apiClient from './apiClient'

// Types
export type ShiftType = 'morning' | 'afternoon' | 'night' | 'rotating'
export type ProductionLineStatus = 'active' | 'idle' | 'maintenance' | 'offline'
export type ProductionOrderStatus = 'pending' | 'in_progress' | 'paused' | 'completed' | 'cancelled'

// Production Line Interfaces
export interface ProductionLine {
  id: number
  line_code: string
  name: string
  description?: string
  status: ProductionLineStatus
  capacity_per_hour?: number
  capacity_unit?: string
  location?: string
  floor?: string
  created_at: string
  updated_at: string
}

export interface CreateProductionLineRequest {
  line_code: string
  name: string
  description?: string
  capacity_per_hour?: number
  capacity_unit?: string
  location?: string
  floor?: string
}

export interface UpdateProductionLineRequest {
  name?: string
  description?: string
  status?: ProductionLineStatus
  capacity_per_hour?: number
  capacity_unit?: string
  location?: string
  floor?: string
}

// Production Line Equipment Station Interfaces
export interface ProductionLineEquipmentStation {
  id: number
  production_line_id: number
  equipment_id: number
  sequence_order: number
  station_name?: string
  operators?: number[]
  cycle_time_minutes?: number
  notes?: string
  created_at: string
  updated_at: string
  // Enriched data from backend
  equipment?: {
    id: number
    name: string
    equipment_id: string
    status?: string
    location?: string
  }
  operators_data?: Array<{
    id: number
    employee_id: string
    full_name: string
    position?: string
  }>
}

export interface CreateEquipmentStationRequest {
  production_line_id: number
  equipment_id: number
  sequence_order: number
  station_name?: string
  operators?: number[]
  cycle_time_minutes?: number
  notes?: string
}

export interface UpdateEquipmentStationRequest {
  sequence_order?: number
  station_name?: string
  operators?: number[]
  cycle_time_minutes?: number
  notes?: string
}

// Shift Interfaces
export interface Shift {
  id: number
  production_line_id: number
  shift_type: ShiftType
  start_time: string
  end_time: string
  team_leader_id?: number
  operators?: number[]
  active_days?: number[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateShiftRequest {
  production_line_id: number
  shift_type: ShiftType
  start_time: string
  end_time: string
  team_leader_id?: number
  operators?: number[]
  active_days?: number[]
  is_active?: boolean
}

export interface UpdateShiftRequest {
  shift_type?: ShiftType
  start_time?: string
  end_time?: string
  team_leader_id?: number
  operators?: number[]
  active_days?: number[]
  is_active?: boolean
}

// Production Order Interfaces
export interface ProductionOrder {
  id: number
  order_number: string
  production_line_id: number
  product_name: string
  product_code?: string
  target_quantity: number
  produced_quantity: number
  unit: string
  defect_quantity?: number
  status: ProductionOrderStatus
  priority: number
  scheduled_start?: string
  scheduled_end?: string
  actual_start?: string
  actual_end?: string
  shift_id?: number
  supervisor_id?: number
  notes?: string
  completion_notes?: string
  created_at: string
  updated_at: string
}

export interface CreateProductionOrderRequest {
  production_line_id: number
  product_name: string
  product_code?: string
  target_quantity: number
  unit: string
  priority?: number
  scheduled_start?: string
  scheduled_end?: string
  shift_id?: number
  notes?: string
}

export interface UpdateProductionOrderRequest {
  product_name?: string
  product_code?: string
  target_quantity?: number
  produced_quantity?: number
  defect_quantity?: number
  unit?: string
  status?: ProductionOrderStatus
  priority?: number
  scheduled_start?: string
  scheduled_end?: string
  shift_id?: number
  supervisor_id?: number
  notes?: string
  completion_notes?: string
}

// Packaging Order Interfaces
export interface PackagingOrder {
  id: number
  order_number: string
  production_order_id?: number
  product_name: string
  product_code?: string
  target_quantity: number
  packaged_quantity: number
  unit: string
  packaging_type?: string
  packaging_material?: string
  units_per_package?: number
  status: ProductionOrderStatus
  scheduled_start?: string
  scheduled_end?: string
  actual_start?: string
  actual_end?: string
  assigned_to?: number
  notes?: string
  created_at: string
  updated_at: string
}

export interface CreatePackagingOrderRequest {
  production_order_id?: number
  product_name: string
  product_code?: string
  target_quantity: number
  unit: string
  packaging_type?: string
  packaging_material?: string
  units_per_package?: number
  scheduled_start?: string
  scheduled_end?: string
  assigned_to?: number
  notes?: string
}

export interface UpdatePackagingOrderRequest {
  product_name?: string
  product_code?: string
  target_quantity?: number
  packaged_quantity?: number
  unit?: string
  packaging_type?: string
  packaging_material?: string
  units_per_package?: number
  status?: ProductionOrderStatus
  scheduled_start?: string
  scheduled_end?: string
  assigned_to?: number
  notes?: string
}

// Statistics Interfaces
export interface ProductionLineStatistics {
  total: number
  active: number
  idle: number
  maintenance: number
}

export interface ProductionOrderStatistics {
  total: number
  pending: number
  in_progress: number
  completed: number
  paused: number
  total_produced: number
  total_target: number
  completion_rate: number
}

export interface PackagingStatistics {
  total: number
  pending: number
  in_progress: number
  completed: number
  total_packaged: number
}

// Production Line Service
class ProductionLineService {
  private baseUrl = '/api/v1/production/lines'

  async getAll(filters: { page?: number; limit?: number; search?: string; status?: ProductionLineStatus } = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.status) params.append('status', filters.status)

    return apiClient.get<{
      success: boolean
      data: ProductionLine[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(`${this.baseUrl}?${params.toString()}`)
  }

  async getStatistics() {
    return apiClient.get<ProductionLineStatistics>(`${this.baseUrl}/statistics`)
  }

  async getById(id: number) {
    return apiClient.get<ProductionLine>(`${this.baseUrl}/${id}`)
  }

  async create(data: CreateProductionLineRequest) {
    return apiClient.post<ProductionLine>(this.baseUrl, data)
  }

  async update(id: number, data: UpdateProductionLineRequest) {
    return apiClient.put<ProductionLine>(`${this.baseUrl}/${id}`, data)
  }

  async delete(id: number) {
    return apiClient.delete(`${this.baseUrl}/${id}`)
  }

  async getEquipmentStations(lineId: number) {
    return apiClient.get<ProductionLineEquipmentStation[]>(`${this.baseUrl}/${lineId}/equipment`)
  }

  async addEquipmentStation(lineId: number, data: CreateEquipmentStationRequest) {
    return apiClient.post<ProductionLineEquipmentStation>(
      `${this.baseUrl}/${lineId}/equipment`,
      data
    )
  }

  async updateEquipmentStation(stationId: number, data: UpdateEquipmentStationRequest) {
    return apiClient.put<ProductionLineEquipmentStation>(
      `/api/v1/production/equipment-stations/${stationId}`,
      data
    )
  }

  async deleteEquipmentStation(stationId: number) {
    return apiClient.delete(`/api/v1/production/equipment-stations/${stationId}`)
  }

  async reorderEquipmentStations(lineId: number, stationOrders: Array<{id: number, sequence_order: number}>) {
    return apiClient.post<ProductionLineEquipmentStation[]>(
      `${this.baseUrl}/${lineId}/equipment/reorder`,
      stationOrders
    )
  }
}

// Shift Service
class ShiftService {
  private baseUrl = '/api/v1/production'

  async getByLine(lineId: number) {
    return apiClient.get<Shift[]>(`${this.baseUrl}/lines/${lineId}/shifts`)
  }

  async getById(id: number) {
    return apiClient.get<Shift>(`${this.baseUrl}/shifts/${id}`)
  }

  async create(data: CreateShiftRequest) {
    return apiClient.post<Shift>(`${this.baseUrl}/shifts`, data)
  }

  async update(id: number, data: UpdateShiftRequest) {
    return apiClient.put<Shift>(`${this.baseUrl}/shifts/${id}`, data)
  }

  async delete(id: number) {
    return apiClient.delete(`${this.baseUrl}/shifts/${id}`)
  }
}

// Production Order Service
class ProductionOrderService {
  private baseUrl = '/api/v1/production/orders'

  async getAll(filters: { page?: number; limit?: number; search?: string; status?: ProductionOrderStatus; line_id?: number } = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.status) params.append('status', filters.status)
    if (filters.line_id) params.append('line_id', filters.line_id.toString())

    return apiClient.get<{
      success: boolean
      data: ProductionOrder[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(`${this.baseUrl}?${params.toString()}`)
  }

  async getStatistics() {
    return apiClient.get<ProductionOrderStatistics>(`${this.baseUrl}/statistics`)
  }

  async getById(id: number) {
    return apiClient.get<ProductionOrder>(`${this.baseUrl}/${id}`)
  }

  async create(data: CreateProductionOrderRequest) {
    return apiClient.post<ProductionOrder>(this.baseUrl, data)
  }

  async update(id: number, data: UpdateProductionOrderRequest) {
    return apiClient.put<ProductionOrder>(`${this.baseUrl}/${id}`, data)
  }

  async delete(id: number) {
    return apiClient.delete(`${this.baseUrl}/${id}`)
  }
}

// Packaging Order Service
class PackagingOrderService {
  private baseUrl = '/api/v1/production/packaging'

  async getAll(filters: { page?: number; limit?: number; search?: string; status?: ProductionOrderStatus } = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.status) params.append('status', filters.status)

    return apiClient.get<{
      success: boolean
      data: PackagingOrder[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(`${this.baseUrl}?${params.toString()}`)
  }

  async getStatistics() {
    return apiClient.get<PackagingStatistics>(`${this.baseUrl}/statistics`)
  }

  async getById(id: number) {
    return apiClient.get<PackagingOrder>(`${this.baseUrl}/${id}`)
  }

  async create(data: CreatePackagingOrderRequest) {
    return apiClient.post<PackagingOrder>(this.baseUrl, data)
  }

  async update(id: number, data: UpdatePackagingOrderRequest) {
    return apiClient.put<PackagingOrder>(`${this.baseUrl}/${id}`, data)
  }

  async delete(id: number) {
    return apiClient.delete(`${this.baseUrl}/${id}`)
  }
}

export const productionLineService = new ProductionLineService()
export const shiftService = new ShiftService()
export const productionOrderService = new ProductionOrderService()
export const packagingOrderService = new PackagingOrderService()
