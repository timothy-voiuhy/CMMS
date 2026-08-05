import apiClient from './apiClient'

export type SalesOrderStatus = 'draft' | 'confirmed' | 'partially_fulfilled' | 'fulfilled' | 'cancelled'
export type SalesOrderLineStatus = 'pending' | 'partially_fulfilled' | 'fulfilled' | 'cancelled'
export type SalesOrderPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface Customer {
  id: number
  customer_code: string
  name: string
  contact_person?: string
  email?: string
  phone?: string
  billing_address?: string
  shipping_address?: string
  tax_id?: string
  payment_terms?: string
  credit_limit?: number
  is_active: boolean
  notes?: string
  created_at: string
  updated_at: string
}

export interface CreateCustomerRequest {
  customer_code?: string
  name: string
  contact_person?: string
  email?: string
  phone?: string
  billing_address?: string
  shipping_address?: string
  tax_id?: string
  payment_terms?: string
  credit_limit?: number
  is_active?: boolean
  notes?: string
}

export type UpdateCustomerRequest = Partial<CreateCustomerRequest>

export interface CustomerFilters {
  page?: number
  limit?: number
  search?: string
  include_inactive?: boolean
}

export interface CustomerSummary {
  id: number
  customer_code: string
  name: string
  contact_person?: string
  email?: string
  phone?: string
}

export interface InventoryItemSalesSummary {
  id: number
  item_code: string
  name: string
  unit_of_measure: string
  quantity: number
  unit_cost?: number
  location?: string
}

export interface SalesOrderItem {
  id: number
  sales_order_id: number
  item_id: number
  item_code: string
  item_name: string
  ordered_quantity: number
  fulfilled_quantity: number
  unit_of_measure: string
  unit_price: number
  tax_rate: number
  discount_amount: number
  line_total: number
  notes?: string
  status: SalesOrderLineStatus
  item?: InventoryItemSalesSummary
  created_at: string
  updated_at: string
}

export interface SalesOrder {
  id: number
  order_number: string
  customer_id: number
  customer?: CustomerSummary
  status: SalesOrderStatus
  priority: SalesOrderPriority
  order_date?: string
  requested_delivery_date?: string
  currency: string
  subtotal: number
  tax_amount: number
  discount_amount: number
  total_amount: number
  created_by: number
  confirmed_by?: number
  confirmed_at?: string
  fulfilled_by?: number
  fulfilled_at?: string
  cancelled_by?: number
  cancelled_at?: string
  cancellation_reason?: string
  notes?: string
  line_count: number
  items?: SalesOrderItem[]
  created_at: string
  updated_at: string
}

export interface CreateSalesOrderLine {
  item_id: number
  ordered_quantity: number
  unit_price: number
  tax_rate?: number
  discount_amount?: number
  notes?: string
}

export interface CreateSalesOrderRequest {
  customer_id: number
  priority: SalesOrderPriority
  order_date?: string
  requested_delivery_date?: string
  currency: string
  notes?: string
  items: CreateSalesOrderLine[]
}

export type UpdateSalesOrderRequest = Partial<Omit<CreateSalesOrderRequest, 'items'>> & {
  items?: CreateSalesOrderLine[]
}

export interface SalesOrderFilters {
  page?: number
  limit?: number
  search?: string
  status?: SalesOrderStatus
  priority?: SalesOrderPriority
  customer_id?: number
}

export interface SalesStatistics {
  total_orders: number
  draft: number
  confirmed: number
  partially_fulfilled: number
  fulfilled: number
  total_revenue: number
  open_value: number
  active_customers: number
}

export interface FulfillSalesOrderRequest {
  items: {
    line_id: number
    quantity: number
  }[]
  notes?: string
}

export interface CancelSalesOrderRequest {
  reason: string
}

interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

class SalesService {
  private baseUrl = '/api/v1/sales'

  async getStatistics() {
    return apiClient.get<SalesStatistics>(`${this.baseUrl}/statistics`)
  }

  async getCustomers(filters: CustomerFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.include_inactive) params.append('include_inactive', 'true')

    return apiClient.get<PaginatedResponse<Customer>>(`${this.baseUrl}/customers?${params.toString()}`)
  }

  async getCustomerById(id: number) {
    return apiClient.get<Customer>(`${this.baseUrl}/customers/${id}`)
  }

  async createCustomer(data: CreateCustomerRequest) {
    return apiClient.post<Customer>(`${this.baseUrl}/customers`, data)
  }

  async updateCustomer(id: number, data: UpdateCustomerRequest) {
    return apiClient.put<Customer>(`${this.baseUrl}/customers/${id}`, data)
  }

  async deleteCustomer(id: number) {
    return apiClient.delete(`${this.baseUrl}/customers/${id}`)
  }

  async getOrders(filters: SalesOrderFilters = {}) {
    const params = new URLSearchParams()
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.status) params.append('status', filters.status)
    if (filters.priority) params.append('priority', filters.priority)
    if (filters.customer_id) params.append('customer_id', filters.customer_id.toString())

    return apiClient.get<PaginatedResponse<SalesOrder>>(`${this.baseUrl}/orders?${params.toString()}`)
  }

  async getOrderById(id: number) {
    return apiClient.get<SalesOrder>(`${this.baseUrl}/orders/${id}`)
  }

  async createOrder(data: CreateSalesOrderRequest) {
    return apiClient.post<SalesOrder>(`${this.baseUrl}/orders`, data)
  }

  async updateOrder(id: number, data: UpdateSalesOrderRequest) {
    return apiClient.put<SalesOrder>(`${this.baseUrl}/orders/${id}`, data)
  }

  async confirmOrder(id: number) {
    return apiClient.post<SalesOrder>(`${this.baseUrl}/orders/${id}/confirm`)
  }

  async fulfillOrder(id: number, data: FulfillSalesOrderRequest) {
    return apiClient.post<SalesOrder>(`${this.baseUrl}/orders/${id}/fulfill`, data)
  }

  async cancelOrder(id: number, data: CancelSalesOrderRequest) {
    return apiClient.post<SalesOrder>(`${this.baseUrl}/orders/${id}/cancel`, data)
  }
}

export const salesService = new SalesService()
