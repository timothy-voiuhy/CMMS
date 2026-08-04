/**
 * Permission Hooks
 * React hooks for checking permissions in components.
 */

import { useMemo } from 'react'
import { useAuthStore } from '../store/authStore'

/**
 * Check if the current user has a specific permission.
 * @param permission - The permission string to check (e.g., 'equipment.create')
 * @returns boolean
 */
export function usePermission(permission: string): boolean {
  const { user } = useAuthStore()

  return useMemo(() => {
    if (!user) return false
    if (user.role === 'admin') return true
    const perms = user.permissions || []
    return perms.includes(permission) || perms.includes('*') || perms.includes('admin.full_access')
  }, [user, permission])
}

/**
 * Check if the current user has ANY of the specified permissions.
 * @param permissions - Array of permission strings
 * @returns boolean
 */
export function useHasAnyPermission(permissions: string[]): boolean {
  const { user } = useAuthStore()

  return useMemo(() => {
    if (!user) return false
    if (user.role === 'admin') return true
    const perms = user.permissions || []
    if (perms.includes('*') || perms.includes('admin.full_access')) return true
    return permissions.some((p) => perms.includes(p))
  }, [user, permissions])
}

/**
 * Check if the current user has ALL of the specified permissions.
 * @param permissions - Array of permission strings
 * @returns boolean
 */
export function useHasAllPermissions(permissions: string[]): boolean {
  const { user } = useAuthStore()

  return useMemo(() => {
    if (!user) return false
    if (user.role === 'admin') return true
    const perms = user.permissions || []
    if (perms.includes('*') || perms.includes('admin.full_access')) return true
    return permissions.every((p) => perms.includes(p))
  }, [user, permissions])
}

/**
 * Get the full permissions array and helper functions.
 * Useful when you need multiple permission checks in one component.
 */
export function usePermissions() {
  const { user, hasPermission, hasAnyPermission, hasAllPermissions } = useAuthStore()

  const permissions = useMemo(() => user?.permissions || [], [user])

  return {
    permissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isAdmin: user?.role === 'admin',
  }
}
