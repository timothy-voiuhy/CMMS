import apiClient from './apiClient'

// ==================== CATEGORY TYPES ====================

export interface InventoryCategory {
  id: number
  name: string
  description?: string
  parent_id?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface InventoryCategoryTree extends InventoryCategory {
  children: InventoryCategoryTree[]
}

export interface CreateInventoryCategoryRequest {
  name: string
  description?: string
  parent_id?: number
  is_active?: boolean
}

export interface UpdateInventoryCategoryRequest {
  name?: string
  description?: string
  parent_id?: number
  is_active?: boolean
}

// ==================== ITEM TYPES ====================

export type TransactionType = 'receipt' | 'issue' | 'transfer' | 'adjustment' | 'return' | 'scrap'

export interface InventoryItem {
  id: number
  item_code: string
  name: string
  description?: string
  category_id: number
  category?: InventoryCategory
  unit_of_measure: string
  quantity: number
  min_quantity?: number
  max_quantity?: number
  reorder_point?: number
  unit_cost?: number
  location?: string
  supplier?: string
  batch_number?: string
  expiry_date?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface InventoryTransaction {
  id: number
  item_id: number
  transaction_type: TransactionType
  quantity: number
  unit_cost?: number
  reference_number?: string
  notes?: string
  performed_by?: number
  created_at: string
}

export interface CreateInventoryItemRequest {
  item_code: string
  name: string
  description?: string
  category_id: number
  unit_of_measure: string
  quantity?: number
  min_quantity?: number
  max_quantity?: number
  reorder_point?: number
  unit_cost?: number
  location?: string
  supplier?: string
  batch_number?: string
  expiry_date?: string
  notes?: string
}

export interface UpdateInventoryItemRequest {
  name?: string
  description?: string
  category_id?: number
  unit_of_measure?: string
  min_quantity?: number
  max_quantity?: number
  reorder_point?: number
  unit_cost?: number
  location?: string
  supplier?: string
  notes?: string
}

export interface InventoryFilters {
  page?: number
  limit?: number
  search?: string
  category_id?: number
  low_stock?: boolean
}

export interface InventoryStatistics {
  total_items: number
  low_stock_count: number
  out_of_stock_count: number
  total_value: number
  category_counts: Record<string, number>
}

export interface AdjustQuantityRequest {
  quantity: number
  transaction_type: TransactionType
  notes?: string
  reference?: string
}

// ==================== REQUISITION TYPES ====================

export type RequisitionStatus =
  | 'draft'
  | 'submitted'
  | 'approved'
  | 'rejected'
  | 'partially_fulfilled'
  | 'fulfilled'
  | 'cancelled'

export type RequisitionLineStatus =
  | 'pending'
  | 'approved'
  | 'partially_fulfilled'
  | 'fulfilled'
  | 'rejected'
  | 'cancelled'

export type RequisitionPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface InventoryItemSummary {
  id: number
  item_code: string
  name: string
  unit_of_measure: string
  quantity: number
  location?: string
}

export interface InventoryRequisitionItem {
  id: number
  requisition_id: number
  item_id: number
  requested_quantity: number
  approved_quantity?: number
  fulfilled_quantity: number
  unit_of_measure: string
  notes?: string
  status: RequisitionLineStatus
  item?: InventoryItemSummary
  created_at: string
  updated_at: string
}

export interface InventoryRequisition {
  id: number
  requisition_number: string
  title: string
  description?: string
  status: RequisitionStatus
  priority: RequisitionPriority
  needed_by?: string
  department?: string
  work_order_id?: number
  production_order_id?: number
  requested_by: number
  approver_id?: number
  assigned_approver?: {
    id: number
    username: string
    full_name: string
    email: string
  }
  approved_by?: number
  approved_at?: string
  fulfilled_by?: number
  fulfilled_at?: string
  rejection_reason?: string
  notes?: string
  line_count: number
  items?: InventoryRequisitionItem[]
  created_at: string
  updated_at: string
}

export interface CreateInventoryRequisitionLine {
  item_id: number
  requested_quantity: number
  notes?: string
}

export interface CreateInventoryRequisitionRequest {
  title: string
  description?: string
  priority: RequisitionPriority
  needed_by?: string
  department?: string
  work_order_id?: number
  production_order_id?: number
  approver_id?: number
  notes?: string
  items: CreateInventoryRequisitionLine[]
}

export type UpdateInventoryRequisitionRequest = Partial<Omit<CreateInventoryRequisitionRequest, 'items'>> & {
  items?: CreateInventoryRequisitionLine[]
}

export interface InventoryRequisitionFilters {
  page?: number
  limit?: number
  search?: string
  status?: RequisitionStatus
  priority?: RequisitionPriority
  requested_by?: number
  work_order_id?: number
  production_order_id?: number
}

export interface ApproveRequisitionRequest {
  items?: {
    line_id: number
    approved_quantity: number
  }[]
  notes?: string
}

export interface RequisitionApprover {
  id: number
  username: string
  full_name: string
  email: string
}

export interface RejectRequisitionRequest {
  reason: string
}

export interface FulfillRequisitionRequest {
  items: {
    line_id: number
    quantity: number
  }[]
  notes?: string
}

class InventoryService {
  private baseUrl = '/api/v1/inventory'

  // ==================== CATEGORY METHODS ====================

  async getCategories(includeInactive = false) {
    const params = new URLSearchParams()
    if (includeInactive) params.append('include_inactive', 'true')
    return apiClient.get<InventoryCategory[]>(`${this.baseUrl}/categories?${params.toString()}`)
  }

  async getCategoryTree() {
    return apiClient.get<InventoryCategoryTree[]>(`${this.baseUrl}/categories/tree`)
  }

  async getCategoryById(id: number) {
    return apiClient.get<InventoryCategory>(`${this.baseUrl}/categories/${id}`)
  }

  async createCategory(data: CreateInventoryCategoryRequest) {
    return apiClient.post<InventoryCategory>(`${this.baseUrl}/categories`, data)
  }

  async updateCategory(id: number, data: UpdateInventoryCategoryRequest) {
    return apiClient.put<InventoryCategory>(`${this.baseUrl}/categories/${id}`, data)
  }

  async deleteCategory(id: number) {
    return apiClient.delete(`${this.baseUrl}/categories/${id}`)
  }

  // ==================== ITEM METHODS ====================

  async getAll(filters: InventoryFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.category_id) params.append('category_id', filters.category_id.toString())
    if (filters.low_stock) params.append('low_stock', 'true')

    const url = `${this.baseUrl}/?${params.toString()}`
    return apiClient.get<{
      success: boolean
      data: InventoryItem[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(url)
  }

  async getStatistics() {
    return apiClient.get<InventoryStatistics>(`${this.baseUrl}/statistics`)
  }

  async getById(id: number) {
    return apiClient.get<InventoryItem>(`${this.baseUrl}/${id}`)
  }

  async create(data: CreateInventoryItemRequest) {
    return apiClient.post<InventoryItem>(this.baseUrl, data)
  }

  async update(id: number, data: UpdateInventoryItemRequest) {
    return apiClient.put<InventoryItem>(`${this.baseUrl}/${id}`, data)
  }

  async delete(id: number) {
    return apiClient.delete(`${this.baseUrl}/${id}`)
  }

  async adjustQuantity(id: number, data: AdjustQuantityRequest) {
    return apiClient.post<InventoryItem>(`${this.baseUrl}/${id}/adjust`, data)
  }

  async getTransactions(id: number, page: number = 1, limit: number = 20) {
    return apiClient.get<InventoryTransaction[]>(
      `${this.baseUrl}/${id}/transactions?page=${page}&limit=${limit}`
    )
  }

  async getLowStockItems() {
    return apiClient.get<InventoryItem[]>(`${this.baseUrl}/low-stock`)
  }

  // ==================== REQUISITION METHODS ====================

  async getRequisitions(filters: InventoryRequisitionFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.status) params.append('status', filters.status)
    if (filters.priority) params.append('priority', filters.priority)
    if (filters.requested_by) params.append('requested_by', filters.requested_by.toString())
    if (filters.work_order_id) params.append('work_order_id', filters.work_order_id.toString())
    if (filters.production_order_id) params.append('production_order_id', filters.production_order_id.toString())

    return apiClient.get<{
      success: boolean
      data: InventoryRequisition[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>(`${this.baseUrl}/requisitions?${params.toString()}`)
  }

  async getRequisitionById(id: number) {
    return apiClient.get<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}`)
  }

  async createRequisition(data: CreateInventoryRequisitionRequest) {
    return apiClient.post<InventoryRequisition>(`${this.baseUrl}/requisitions`, data)
  }

  async updateRequisition(id: number, data: UpdateInventoryRequisitionRequest) {
    return apiClient.put<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}`, data)
  }

  async submitRequisition(id: number) {
    return apiClient.post<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}/submit`)
  }

  async submitRequisitionWithApprover(id: number, approver_id: number) {
    return apiClient.post<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}/submit`, { approver_id })
  }

  async getRequisitionApprovers() {
    return apiClient.get<RequisitionApprover[]>(`${this.baseUrl}/requisitions/approvers`)
  }

  async assignRequisitionApprover(id: number, approver_id: number) {
    return apiClient.patch<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}/approver`, { approver_id })
  }

  async approveRequisition(id: number, data: ApproveRequisitionRequest) {
    return apiClient.post<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}/approve`, data)
  }

  async rejectRequisition(id: number, data: RejectRequisitionRequest) {
    return apiClient.post<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}/reject`, data)
  }

  async fulfillRequisition(id: number, data: FulfillRequisitionRequest) {
    return apiClient.post<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}/fulfill`, data)
  }

  async cancelRequisition(id: number) {
    return apiClient.post<InventoryRequisition>(`${this.baseUrl}/requisitions/${id}/cancel`)
  }
}

export const inventoryService = new InventoryService()
