/**
 * Permission Type Definitions for RBAC
 */

export type Permission = string

export interface PermissionDefinition {
  key: string
  name: string
  description: string
  category: string
  implies: string[]
}

export interface PermissionRegistry {
  permissions: PermissionDefinition[]
  categories: string[]
}

export interface PermissionsConfig {
  version: string
  permissions: Permission[]
  template?: string
  custom: boolean
  last_modified: string
}

export interface RoleTemplate {
  key: string
  name: string
  description: string
  level: number
  category: string
  permissions: Permission[]
}

export interface RoleWithPermissions {
  id: number
  name: string
  description: string
  level: number
  category: string
  permissions_json: string
  parsed_permissions: Permission[]
  is_active: boolean
  is_system_role: boolean
  created_at: string
  updated_at: string
}

export interface RolePermissionsUpdate {
  permissions: Permission[]
  template?: string
  custom: boolean
}

export interface CreateRoleFromTemplate {
  name: string
  template: string
  description?: string
  level?: number
  category?: string
}
