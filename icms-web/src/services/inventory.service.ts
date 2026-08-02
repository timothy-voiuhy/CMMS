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
}

export const inventoryService = new InventoryService()
