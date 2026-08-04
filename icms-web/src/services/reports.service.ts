import apiClient from './apiClient'

// ============= Types =============

export interface EquipmentSummary {
  total_equipment: number
  by_status: Array<{ status: string; count: number }>
  by_type: Array<{ type: string; count: number }>
  average_utilization: number
  critical_equipment: number
}

export interface EquipmentUtilization {
  period_days: number
  equipment: Array<{
    code: string
    name: string
    type: string
    utilization: number
    status: string
  }>
}

export interface MaintenanceSummary {
  start_date: string
  end_date: string
  total_maintenance: number
  by_type: Array<{ type: string; count: number }>
  by_priority: Array<{ priority: string; count: number }>
  average_cost: number
}

export interface MaintenanceDowntime {
  period_days: number
  equipment_downtime: Array<{
    equipment_code: string
    equipment_name: string
    maintenance_count: number
    total_downtime_hours: number
  }>
}

export interface InventorySummary {
  total_items: number
  total_value: number
  low_stock_items: number
  out_of_stock: number
  by_category: Array<{
    category: string
    count: number
    value: number
  }>
}

export interface InventoryMovements {
  start_date: string
  end_date: string
  transactions: Array<{
    type: string
    count: number
    total_quantity: number
  }>
}

export interface LowStockItem {
  id: number
  item_code: string
  name: string
  category: string
  quantity: number
  unit: string
  reorder_level: number
  reorder_quantity: number
  shortage: number
}

export interface LowStockReport {
  low_stock_items: LowStockItem[]
}

export interface ProductionSummary {
  start_date: string
  end_date: string
  total_orders: number
  by_status: Array<{ status: string; count: number }>
  total_quantity_produced: number
  active_lines: number
}

export interface ProductionEfficiency {
  period_days: number
  production_lines: Array<{
    line_code: string
    line_name: string
    orders_count: number
    total_produced: number
    average_efficiency: number
  }>
}

export interface QualitySummary {
  start_date: string
  end_date: string
  total_inspections: number
  by_result: Array<{ result: string; count: number }>
  total_ncrs: number
  ncrs_by_severity: Array<{ severity: string; count: number }>
  pass_rate: number
}

export interface WorkOrdersSummary {
  start_date: string
  end_date: string
  total_work_orders: number
  by_status: Array<{ status: string; count: number }>
  by_priority: Array<{ priority: string; count: number }>
  overdue: number
}

export interface PersonnelSummary {
  total_craftsmen: number
  active_craftsmen: number
  by_specialization: Array<{ specialization: string; count: number }>
  average_experience_years: number
}

export interface FinancialSummary {
  start_date: string
  end_date: string
  maintenance_cost: number
  inventory_value: number
  inventory_transactions: Array<{
    type: string
    value: number
  }>
}

// ============= Service =============

class ReportsService {
  // Equipment Reports
  async getEquipmentSummary(): Promise<EquipmentSummary> {
    return await apiClient.get('/api/v1/reports/equipment/summary')
  }

  async getEquipmentUtilization(days: number = 30, equipmentType?: string): Promise<EquipmentUtilization> {
    const params: any = { days }
    if (equipmentType) params.equipment_type = equipmentType
    return await apiClient.get('/api/v1/reports/equipment/utilization', { params })
  }

  // Maintenance Reports
  async getMaintenanceSummary(startDate?: string, endDate?: string): Promise<MaintenanceSummary> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return await apiClient.get('/api/v1/reports/maintenance/summary', { params })
  }

  async getMaintenanceDowntime(days: number = 30): Promise<MaintenanceDowntime> {
    return await apiClient.get('/api/v1/reports/maintenance/downtime', { params: { days } })
  }

  // Inventory Reports
  async getInventorySummary(): Promise<InventorySummary> {
    return await apiClient.get('/api/v1/reports/inventory/summary')
  }

  async getInventoryMovements(startDate?: string, endDate?: string, transactionType?: string): Promise<InventoryMovements> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    if (transactionType) params.transaction_type = transactionType
    return await apiClient.get('/api/v1/reports/inventory/movements', { params })
  }

  async getLowStockReport(): Promise<LowStockReport> {
    return await apiClient.get('/api/v1/reports/inventory/low-stock')
  }

  // Production Reports
  async getProductionSummary(startDate?: string, endDate?: string): Promise<ProductionSummary> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return await apiClient.get('/api/v1/reports/production/summary', { params })
  }

  async getProductionEfficiency(days: number = 30): Promise<ProductionEfficiency> {
    return await apiClient.get('/api/v1/reports/production/efficiency', { params: { days } })
  }

  // Quality Reports
  async getQualitySummary(startDate?: string, endDate?: string): Promise<QualitySummary> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return await apiClient.get('/api/v1/reports/quality/summary', { params })
  }

  // Work Orders Reports
  async getWorkOrdersSummary(startDate?: string, endDate?: string): Promise<WorkOrdersSummary> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return await apiClient.get('/api/v1/reports/work-orders/summary', { params })
  }

  // Personnel Reports
  async getPersonnelSummary(): Promise<PersonnelSummary> {
    return await apiClient.get('/api/v1/reports/personnel/summary')
  }

  // Financial Reports
  async getFinancialSummary(startDate?: string, endDate?: string): Promise<FinancialSummary> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return await apiClient.get('/api/v1/reports/financial/summary', { params })
  }
}

export const reportsService = new ReportsService()
