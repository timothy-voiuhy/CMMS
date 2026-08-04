/**
 * Global Type Definitions for ICMS
 */

// Common types
export type Status = 'Active' | 'Inactive' | 'Pending' | 'Archived'
export type Priority = 'Low' | 'Medium' | 'High' | 'Critical'
export type Role = 'admin' | 'craftsman' | 'inventory' | 'production' | 'quality' | 'manager'

// User Types
export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: 'ADMIN' | 'MANAGER' | 'CRAFTSMAN' | 'INVENTORY' | 'QUALITY' | 'PRODUCTION' | 'READONLY'
  is_active: boolean
  phone?: string
  created_at: string
  updated_at: string
}

// Equipment Types
export type Equipment = {
  id: number
  name: string
  equipment_id: string
  category?: string
  manufacturer?: string
  model?: string
  serial_number?: string
  location?: string
  status: 'OPERATIONAL' | 'MAINTENANCE' | 'BREAKDOWN' | 'RETIRED'
  purchase_date?: string
  warranty_expiry?: string
  specifications?: string
  notes?: string
  parent_id?: number
  created_at: string
  updated_at: string
}

export interface EquipmentHistory {
  history_id: number
  equipment_id: number
  date: string
  event_type: string
  description?: string
  performed_by?: string
  notes?: string
}

export interface MaintenanceSchedule {
  task_id: number
  equipment_id: number
  task_name: string
  frequency: number
  frequency_unit: 'days' | 'weeks' | 'months' | 'years'
  last_done?: string
  next_due?: string
  maintenance_procedure?: string
  required_parts?: string
}

// Craftsman Types
export interface Craftsman {
  id: number
  user_id: number
  employee_id: string
  department?: string
  position?: string
  role_id?: number
  role_name?: string
  hire_date?: string
  certification_level?: string
  hourly_rate?: number
  notes?: string
  created_at: string
  updated_at: string
}

export interface CraftsmanSkill {
  id: number
  name: string
  description?: string
  category?: string
  created_at: string
  updated_at: string
}

export interface CraftsmanTraining {
  training_id: number
  craftsman_id: number
  training_name: string
  training_date?: string
  completion_date?: string
  training_provider?: string
  certification_received?: string
  training_status?: string
  notes?: string
}

// Work Order Types
export interface WorkOrder {
  id: number
  work_order_number: string
  title: string
  description?: string
  work_order_type: 'PREVENTIVE' | 'CORRECTIVE' | 'PREDICTIVE' | 'EMERGENCY' | 'MODIFICATION' | 'INSPECTION'
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'
  status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED'
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

export interface MaintenanceReport {
  id: number
  work_order_id: number
  equipment_id: number
  craftsman_id: number
  report_number: string
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
}

// Inventory Types
export interface InventoryItem {
  id: number
  item_code: string
  name: string
  description?: string
  category: 'RAW_MATERIAL' | 'WIP' | 'FINISHED_GOOD' | 'SPARE_PART' | 'TOOL' | 'CONSUMABLE' | 'PACKAGING'
  unit_of_measure: string
  quantity: number
  min_quantity?: number
  max_quantity?: number
  reorder_point?: number
  unit_cost?: number
  location?: string
  supplier?: string
  notes?: string
  batch_number?: string
  expiry_date?: string
  created_at: string
  updated_at: string
}

export interface InventoryCategory {
  category_id: number
  name: string
  description?: string
}

export interface Supplier {
  supplier_id: number
  name: string
  contact_person?: string
  phone?: string
  email?: string
  address?: string
  notes?: string
  status: Status
  created_at: string
  last_modified: string
}

export interface InventoryTransaction {
  id: number
  item_id: number
  transaction_type: 'RECEIPT' | 'ISSUE' | 'TRANSFER' | 'ADJUSTMENT' | 'RETURN' | 'SCRAP'
  quantity: number
  unit_cost?: number
  reference_number?: string
  notes?: string
  performed_by?: number
  created_at: string
  updated_at: string
}

export interface PurchaseOrder {
  po_id: number
  po_number: string
  supplier_id: number
  status: 'Pending' | 'Approved' | 'Ordered' | 'Received' | 'Cancelled'
  total_amount?: number
  created_by: string
  created_at: string
  expected_delivery?: string
  notes?: string
}

// Production Types (future)
export interface ProductionOrder {
  order_id: number
  product_code: string
  product_name: string
  quantity: number
  status: 'Scheduled' | 'In Progress' | 'Completed' | 'On Hold'
  start_date: string
  end_date?: string
  notes?: string
}

// Quality Types (future)
export interface QualityInspection {
  inspection_id: number
  work_order_id?: number
  production_order_id?: number
  inspector_id: number
  inspection_date: string
  result: 'Pass' | 'Fail' | 'Conditional'
  notes?: string
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface ApiError {
  success: false
  message: string
  errors?: Record<string, string[]>
}
