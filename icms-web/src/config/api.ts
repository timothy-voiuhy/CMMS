/**
 * API Configuration
 * Central configuration for all API endpoints and settings
 */

const getDefaultApiUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }

  if (import.meta.env.DEV) {
    return ''
  }

  return `http://${window.location.hostname}:8000`
}

export const API_CONFIG = {
  BASE_URL: getDefaultApiUrl(),
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
}

export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
  },
  
  // Equipment
  EQUIPMENT: {
    LIST: '/equipment',
    DETAIL: (id: string) => `/equipment/${id}`,
    CREATE: '/equipment',
    UPDATE: (id: string) => `/equipment/${id}`,
    DELETE: (id: string) => `/equipment/${id}`,
    HISTORY: (id: string) => `/equipment/${id}/history`,
    TECHNICAL_INFO: (id: string) => `/equipment/${id}/technical-info`,
    MAINTENANCE_SCHEDULE: (id: string) => `/equipment/${id}/maintenance-schedule`,
  },
  
  // Craftsmen
  CRAFTSMEN: {
    LIST: '/craftsmen',
    DETAIL: (id: string) => `/craftsmen/${id}`,
    CREATE: '/craftsmen',
    UPDATE: (id: string) => `/craftsmen/${id}`,
    DELETE: (id: string) => `/craftsmen/${id}`,
    SKILLS: (id: string) => `/craftsmen/${id}/skills`,
    TRAINING: (id: string) => `/craftsmen/${id}/training`,
    WORK_HISTORY: (id: string) => `/craftsmen/${id}/work-history`,
  },
  
  // Inventory
  INVENTORY: {
    LIST: '/inventory',
    DETAIL: (id: string) => `/inventory/${id}`,
    CREATE: '/inventory',
    UPDATE: (id: string) => `/inventory/${id}`,
    DELETE: (id: string) => `/inventory/${id}`,
    TRANSACTIONS: (id: string) => `/inventory/${id}/transactions`,
    LOW_STOCK: '/inventory/low-stock',
    CATEGORIES: '/inventory/categories',
    SUPPLIERS: '/inventory/suppliers',
  },
  
  // Work Orders
  WORK_ORDERS: {
    LIST: '/work-orders',
    DETAIL: (id: string) => `/work-orders/${id}`,
    CREATE: '/work-orders',
    UPDATE: (id: string) => `/work-orders/${id}`,
    DELETE: (id: string) => `/work-orders/${id}`,
    UPDATE_STATUS: (id: string) => `/work-orders/${id}/status`,
    ASSIGN: (id: string) => `/work-orders/${id}/assign`,
    ATTACHMENTS: (id: string) => `/work-orders/${id}/attachments`,
  },
  
  // Maintenance
  MAINTENANCE: {
    REPORTS: '/maintenance/reports',
    REPORT_DETAIL: (id: string) => `/maintenance/reports/${id}`,
    CREATE_REPORT: '/maintenance/reports',
    SCHEDULES: '/maintenance/schedules',
    HISTORY: '/maintenance/history',
  },
  
  // Production
  PRODUCTION: {
    ORDERS: '/production/orders',
    ORDER_DETAIL: (id: string) => `/production/orders/${id}`,
    SCHEDULE: '/production/schedule',
    PERFORMANCE: '/production/performance',
  },
  
  // Quality
  QUALITY: {
    INSPECTIONS: '/quality/inspections',
    INSPECTION_DETAIL: (id: string) => `/quality/inspections/${id}`,
    NCR: '/quality/ncr',
    CAPA: '/quality/capa',
  },
  
  // Reports
  REPORTS: {
    DASHBOARD: '/reports/dashboard',
    EQUIPMENT: '/reports/equipment',
    MAINTENANCE: '/reports/maintenance',
    INVENTORY: '/reports/inventory',
    PRODUCTION: '/reports/production',
    CUSTOM: '/reports/custom',
  },
  
  // Settings
  SETTINGS: {
    SYSTEM: '/settings/system',
    USER_PREFERENCES: '/settings/user',
    ROLES: '/settings/roles',
    PERMISSIONS: '/settings/permissions',
  },
}

export default API_CONFIG
