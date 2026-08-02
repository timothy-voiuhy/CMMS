/**
 * Service Layer
 * Centralized export for all API services
 */

export { default as apiClient } from './apiClient'
export { default as authService } from './auth.service'
export { default as equipmentService } from './equipment.service'
export { default as craftsmanService } from './craftsman.service'
export { workOrderService } from './workOrder.service'
export { default as inventoryService } from './inventory.service'
export { default as maintenanceService } from './maintenance.service'

// Re-export types for convenience
export type * from './auth.service'
export type * from './equipment.service'
export type * from './craftsman.service'
export type * from './workOrder.service'
export type * from './inventory.service'
export type * from './maintenance.service'
