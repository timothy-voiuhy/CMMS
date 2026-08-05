/**
 * Client-side Permission Registry & Resolution
 * Mirror of backend permission definitions for instant UI rendering.
 */

import type { PermissionDefinition } from '../types/permissions'

// ==================== PERMISSION REGISTRY ====================

export const PERMISSION_REGISTRY: Record<string, Omit<PermissionDefinition, 'key'>> = {
  // Dashboard
  'dashboard.view': { name: 'View Dashboard', description: 'Access main dashboard and overview metrics', category: 'Dashboard', implies: [] },

  // Equipment
  'equipment.view': { name: 'View Equipment', description: 'View equipment list and details', category: 'Equipment', implies: [] },
  'equipment.create': { name: 'Create Equipment', description: 'Add new equipment to the system', category: 'Equipment', implies: ['equipment.view'] },
  'equipment.edit': { name: 'Edit Equipment', description: 'Modify existing equipment details', category: 'Equipment', implies: ['equipment.view'] },
  'equipment.delete': { name: 'Delete Equipment', description: 'Remove equipment from the system', category: 'Equipment', implies: ['equipment.view'] },
  'equipment.assign': { name: 'Assign Equipment', description: 'Assign equipment to craftsmen or work orders', category: 'Equipment', implies: ['equipment.view'] },

  // Inventory
  'inventory.view': { name: 'View Inventory', description: 'View inventory items and stock levels', category: 'Inventory', implies: [] },
  'inventory.create': { name: 'Create Inventory Items', description: 'Add new inventory items', category: 'Inventory', implies: ['inventory.view'] },
  'inventory.edit': { name: 'Edit Inventory Items', description: 'Modify inventory item details', category: 'Inventory', implies: ['inventory.view'] },
  'inventory.delete': { name: 'Delete Inventory Items', description: 'Remove inventory items', category: 'Inventory', implies: ['inventory.view'] },
  'inventory.transaction': { name: 'Create Transactions', description: 'Record inventory transactions', category: 'Inventory', implies: ['inventory.view'] },
  'inventory.adjust': { name: 'Adjust Stock Levels', description: 'Perform manual stock adjustments', category: 'Inventory', implies: ['inventory.view', 'inventory.transaction'] },
  'inventory.categories': { name: 'Manage Categories', description: 'Create and manage inventory categories', category: 'Inventory', implies: ['inventory.view'] },
  'inventory.requisitions.view': { name: 'View Requisitions', description: 'View inventory requisitions and request status', category: 'Inventory', implies: ['inventory.view'] },
  'inventory.requisitions.create': { name: 'Create Requisitions', description: 'Create inventory material requests', category: 'Inventory', implies: ['inventory.requisitions.view'] },
  'inventory.requisitions.edit': { name: 'Edit Requisitions', description: 'Modify draft inventory requisitions', category: 'Inventory', implies: ['inventory.requisitions.view'] },
  'inventory.requisitions.submit': { name: 'Submit Requisitions', description: 'Submit draft requisitions for approval', category: 'Inventory', implies: ['inventory.requisitions.view'] },
  'inventory.requisitions.approve': { name: 'Approve Requisitions', description: 'Approve or reject submitted inventory requisitions', category: 'Inventory', implies: ['inventory.requisitions.view'] },
  'inventory.requisitions.fulfill': { name: 'Fulfill Requisitions', description: 'Issue stock against approved inventory requisitions', category: 'Inventory', implies: ['inventory.requisitions.view', 'inventory.transaction'] },
  'inventory.requisitions.cancel': { name: 'Cancel Requisitions', description: 'Cancel inventory requisitions before fulfillment', category: 'Inventory', implies: ['inventory.requisitions.view'] },

  // Production
  'production.view': { name: 'View Production', description: 'View production lines, orders, and packaging', category: 'Production', implies: [] },
  'production.create': { name: 'Create Production Orders', description: 'Create new production orders', category: 'Production', implies: ['production.view'] },
  'production.edit': { name: 'Edit Production Orders', description: 'Modify production order details', category: 'Production', implies: ['production.view'] },
  'production.delete': { name: 'Delete Production Orders', description: 'Remove production orders', category: 'Production', implies: ['production.view'] },
  'production.start': { name: 'Start Production', description: 'Start production orders and lines', category: 'Production', implies: ['production.view'] },
  'production.complete': { name: 'Complete Production', description: 'Mark production orders as completed', category: 'Production', implies: ['production.view'] },
  'production.lines': { name: 'Manage Production Lines', description: 'Create and configure production lines', category: 'Production', implies: ['production.view'] },
  'production.packaging': { name: 'Manage Packaging', description: 'Access and manage packaging operations', category: 'Production', implies: ['production.view'] },

  // Quality
  'quality.view': { name: 'View Quality Records', description: 'View quality inspections and NCRs', category: 'Quality', implies: [] },
  'quality.inspect': { name: 'Perform Inspections', description: 'Create and complete quality inspections', category: 'Quality', implies: ['quality.view'] },
  'quality.ncr_create': { name: 'Create NCRs', description: 'Create Non-Conformance Reports', category: 'Quality', implies: ['quality.view'] },
  'quality.ncr_close': { name: 'Close NCRs', description: 'Review and close Non-Conformance Reports', category: 'Quality', implies: ['quality.view', 'quality.ncr_create'] },
  'quality.approve': { name: 'Approve Quality Records', description: 'Approve quality inspections and reports', category: 'Quality', implies: ['quality.view'] },

  // Maintenance
  'maintenance.view': { name: 'View Maintenance', description: 'View maintenance schedules and reports', category: 'Maintenance', implies: [] },
  'maintenance.create': { name: 'Create Maintenance Records', description: 'Create maintenance schedules and reports', category: 'Maintenance', implies: ['maintenance.view'] },
  'maintenance.edit': { name: 'Edit Maintenance Records', description: 'Modify maintenance records', category: 'Maintenance', implies: ['maintenance.view'] },
  'maintenance.complete': { name: 'Complete Maintenance', description: 'Mark maintenance tasks as completed', category: 'Maintenance', implies: ['maintenance.view'] },
  'maintenance.schedule': { name: 'Schedule Maintenance', description: 'Create and modify maintenance schedules', category: 'Maintenance', implies: ['maintenance.view', 'maintenance.create'] },

  // Work Orders
  'work_orders.view': { name: 'View Work Orders', description: 'View work order list and details', category: 'Work Orders', implies: [] },
  'work_orders.create': { name: 'Create Work Orders', description: 'Create new work orders', category: 'Work Orders', implies: ['work_orders.view'] },
  'work_orders.assign': { name: 'Assign Work Orders', description: 'Assign work orders to craftsmen', category: 'Work Orders', implies: ['work_orders.view'] },
  'work_orders.complete': { name: 'Complete Work Orders', description: 'Mark work orders as completed', category: 'Work Orders', implies: ['work_orders.view'] },
  'work_orders.edit': { name: 'Edit Work Orders', description: 'Modify work order details', category: 'Work Orders', implies: ['work_orders.view'] },
  'work_orders.delete': { name: 'Delete Work Orders', description: 'Remove work orders', category: 'Work Orders', implies: ['work_orders.view'] },

  // Personnel
  'craftsmen.view': { name: 'View Craftsmen', description: 'View craftsmen list and profiles', category: 'Personnel', implies: [] },
  'craftsmen.create': { name: 'Create Craftsmen', description: 'Add new craftsmen to the system', category: 'Personnel', implies: ['craftsmen.view'] },
  'craftsmen.edit': { name: 'Edit Craftsmen', description: 'Modify craftsmen details', category: 'Personnel', implies: ['craftsmen.view'] },
  'craftsmen.delete': { name: 'Delete Craftsmen', description: 'Remove craftsmen from the system', category: 'Personnel', implies: ['craftsmen.view'] },
  'craftsmen.assign_role': { name: 'Assign Roles', description: 'Assign roles to craftsmen', category: 'Personnel', implies: ['craftsmen.view', 'craftsmen.edit'] },

  // Reports
  'reports.view': { name: 'View Reports', description: 'Access basic reporting dashboard', category: 'Reports', implies: [] },
  'reports.equipment': { name: 'Equipment Reports', description: 'View equipment-related reports', category: 'Reports', implies: ['reports.view', 'equipment.view'] },
  'reports.maintenance': { name: 'Maintenance Reports', description: 'View maintenance reports', category: 'Reports', implies: ['reports.view', 'maintenance.view'] },
  'reports.inventory': { name: 'Inventory Reports', description: 'View inventory reports', category: 'Reports', implies: ['reports.view', 'inventory.view'] },
  'reports.production': { name: 'Production Reports', description: 'View production reports', category: 'Reports', implies: ['reports.view', 'production.view'] },
  'reports.quality': { name: 'Quality Reports', description: 'View quality reports', category: 'Reports', implies: ['reports.view', 'quality.view'] },
  'reports.financial': { name: 'Financial Reports', description: 'View financial and cost reports', category: 'Reports', implies: ['reports.view'] },
  'reports.export': { name: 'Export Reports', description: 'Export reports to PDF/Excel', category: 'Reports', implies: ['reports.view'] },

  // Settings
  'settings.view': { name: 'View Settings', description: 'Access settings page', category: 'Settings', implies: [] },
  'settings.company': { name: 'Manage Company Settings', description: 'Edit company profile and preferences', category: 'Settings', implies: ['settings.view'] },
  'settings.users': { name: 'Manage Users', description: 'Create and manage user accounts', category: 'Settings', implies: ['settings.view'] },
  'settings.roles': { name: 'Manage Roles', description: 'Create and configure roles and permissions', category: 'Settings', implies: ['settings.view'] },
  'settings.facilities': { name: 'Manage Facilities', description: 'Manage facilities and departments', category: 'Settings', implies: ['settings.view'] },
  'settings.system': { name: 'System Settings', description: 'Configure system-wide settings', category: 'Settings', implies: ['settings.view'] },

  // Administration
  'admin.full_access': { name: 'Full System Access', description: 'Complete access to all system features', category: 'Administration', implies: ['*'] },
  'admin.audit_logs': { name: 'View Audit Logs', description: 'Access system audit logs', category: 'Administration', implies: [] },
  'admin.backup': { name: 'Backup Management', description: 'Perform system backups and restores', category: 'Administration', implies: [] },
}

// ==================== ROLE TEMPLATES ====================

export const ROLE_TEMPLATES: Record<string, { name: string; description: string; level: number; category: string; permissions: string[] }> = {
  general_manager: { name: 'General Manager', description: 'Complete system access for top management', level: 10, category: 'Management', permissions: ['admin.full_access'] },
  production_manager: { name: 'Production Manager', description: 'Manages production operations', level: 9, category: 'Management', permissions: ['dashboard.view', 'production.*', 'equipment.view', 'equipment.assign', 'inventory.view', 'inventory.transaction', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit', 'inventory.requisitions.approve', 'quality.view', 'maintenance.view', 'work_orders.view', 'work_orders.assign', 'craftsmen.view', 'reports.view', 'reports.production', 'reports.equipment', 'reports.export'] },
  quality_manager: { name: 'Quality Manager', description: 'Manages quality assurance operations', level: 9, category: 'Management', permissions: ['dashboard.view', 'quality.*', 'production.view', 'inventory.view', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit', 'reports.view', 'reports.quality', 'reports.production', 'reports.export', 'craftsmen.view'] },
  maintenance_manager: { name: 'Maintenance Manager', description: 'Manages maintenance operations', level: 8, category: 'Management', permissions: ['dashboard.view', 'maintenance.*', 'work_orders.*', 'equipment.*', 'inventory.view', 'inventory.transaction', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit', 'inventory.requisitions.approve', 'craftsmen.view', 'reports.view', 'reports.maintenance', 'reports.equipment', 'reports.export'] },
  production_team_leader: { name: 'Production Team Leader', description: 'Supervises production team', level: 6, category: 'Supervision', permissions: ['dashboard.view', 'production.view', 'production.start', 'production.complete', 'production.packaging', 'equipment.view', 'inventory.view', 'inventory.transaction', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit', 'inventory.requisitions.approve', 'quality.view', 'work_orders.view', 'craftsmen.view', 'reports.view', 'reports.production'] },
  maintenance_team_leader: { name: 'Maintenance Team Leader', description: 'Supervises maintenance team', level: 6, category: 'Supervision', permissions: ['dashboard.view', 'maintenance.view', 'maintenance.complete', 'work_orders.view', 'work_orders.complete', 'equipment.view', 'equipment.edit', 'inventory.view', 'inventory.transaction', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit', 'inventory.requisitions.approve', 'craftsmen.view', 'reports.view', 'reports.maintenance'] },
  quality_inspector: { name: 'Quality Inspector', description: 'Performs quality inspections', level: 4, category: 'Technical', permissions: ['dashboard.view', 'quality.view', 'quality.inspect', 'quality.ncr_create', 'production.view', 'inventory.view', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit', 'reports.view', 'reports.quality'] },
  maintenance_technician: { name: 'Maintenance Technician', description: 'Performs maintenance work', level: 4, category: 'Technical', permissions: ['dashboard.view', 'maintenance.view', 'maintenance.complete', 'work_orders.view', 'work_orders.complete', 'equipment.view', 'inventory.view', 'inventory.transaction', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit'] },
  machine_operator: { name: 'Machine Operator', description: 'Operates production machinery', level: 3, category: 'Operations', permissions: ['dashboard.view', 'production.view', 'production.start', 'production.complete', 'equipment.view', 'inventory.view', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit', 'quality.view', 'work_orders.view'] },
  inventory_clerk: { name: 'Inventory Clerk', description: 'Manages inventory operations', level: 3, category: 'Operations', permissions: ['dashboard.view', 'inventory.*', 'production.view', 'reports.view', 'reports.inventory'] },
  general_worker: { name: 'General Worker', description: 'Basic view-only access', level: 2, category: 'Operations', permissions: ['dashboard.view', 'production.view', 'equipment.view', 'inventory.view', 'inventory.requisitions.view', 'inventory.requisitions.create', 'inventory.requisitions.submit', 'work_orders.view'] },
  admin: { name: 'System Administrator', description: 'Full system and settings access', level: 10, category: 'Administration', permissions: ['admin.full_access', 'settings.*'] },
}

// ==================== CATEGORY ORDER ====================

export const CATEGORY_ORDER = [
  'Dashboard',
  'Equipment',
  'Inventory',
  'Production',
  'Quality',
  'Maintenance',
  'Work Orders',
  'Personnel',
  'Reports',
  'Settings',
  'Administration',
]

// ==================== PERMISSION RESOLUTION ====================

/**
 * Resolve permissions with inheritance and wildcards.
 * Client-side mirror of backend logic for instant UI updates.
 */
export function resolvePermissions(grantedPermissions: string[]): string[] {
  const allKeys = Object.keys(PERMISSION_REGISTRY)
  const resolved = new Set<string>()

  // Handle full access
  if (grantedPermissions.includes('*') || grantedPermissions.includes('admin.full_access')) {
    return allKeys
  }

  // Handle wildcards
  for (const perm of grantedPermissions) {
    if (perm.endsWith('.*')) {
      const resource = perm.split('.')[0]
      for (const key of allKeys) {
        if (key.startsWith(`${resource}.`)) {
          resolved.add(key)
        }
      }
    } else {
      resolved.add(perm)
    }
  }

  // Resolve implies recursively
  const toProcess = [...resolved]
  while (toProcess.length > 0) {
    const current = toProcess.pop()!
    const def = PERMISSION_REGISTRY[current]
    if (def?.implies) {
      for (const implied of def.implies) {
        if (implied === '*') {
          return allKeys
        }
        if (!resolved.has(implied)) {
          resolved.add(implied)
          toProcess.push(implied)
        }
      }
    }
  }

  return [...resolved].sort()
}

/**
 * Get permissions grouped by category.
 */
export function getPermissionsByCategory(): Record<string, { key: string; name: string; description: string; implies: string[] }[]> {
  const grouped: Record<string, { key: string; name: string; description: string; implies: string[] }[]> = {}

  for (const [key, def] of Object.entries(PERMISSION_REGISTRY)) {
    if (!grouped[def.category]) {
      grouped[def.category] = []
    }
    grouped[def.category].push({ key, name: def.name, description: def.description, implies: def.implies })
  }

  return grouped
}
