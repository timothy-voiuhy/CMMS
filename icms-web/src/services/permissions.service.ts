/**
 * Permission API Service
 * Handles all API calls for permission management.
 */

import apiClient from './apiClient'
import type {
  RoleWithPermissions,
  RolePermissionsUpdate,
  PermissionRegistry,
  RoleTemplate,
  CreateRoleFromTemplate,
} from '../types/permissions'
import type { Role } from './company.service'

const BASE_URL = '/api/v1/company'

export const permissionsService = {
  /**
   * Get role with parsed permissions
   */
  async getRolePermissions(roleId: number): Promise<RoleWithPermissions> {
    return apiClient.get<RoleWithPermissions>(`${BASE_URL}/roles/${roleId}/permissions`)
  },

  /**
   * Update role permissions
   */
  async updateRolePermissions(roleId: number, data: RolePermissionsUpdate): Promise<RoleWithPermissions> {
    return apiClient.put<RoleWithPermissions>(`${BASE_URL}/roles/${roleId}/permissions`, data)
  },

  /**
   * Get complete permission registry
   */
  async getPermissionRegistry(): Promise<PermissionRegistry> {
    return apiClient.get<PermissionRegistry>(`${BASE_URL}/permissions/registry`)
  },

  /**
   * Get available role templates
   */
  async getPermissionTemplates(): Promise<RoleTemplate[]> {
    return apiClient.get<RoleTemplate[]>(`${BASE_URL}/permissions/templates`)
  },

  /**
   * Create a new role from a template
   */
  async createRoleFromTemplate(data: CreateRoleFromTemplate): Promise<Role> {
    return apiClient.post<Role>(`${BASE_URL}/roles/from-template`, data)
  },
}

export default permissionsService
