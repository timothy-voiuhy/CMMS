/**
 * Permission Guard Components
 * Components that conditionally render children based on user permissions.
 */

import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { usePermission, useHasAnyPermission } from '../../hooks/usePermission'

interface PermissionGuardProps {
  /** Single permission to check */
  permission?: string
  /** Multiple permissions — user needs ANY of these */
  anyOf?: string[]
  /** Multiple permissions — user needs ALL of these */
  allOf?: string[]
  /** Content to render when access is denied (defaults to nothing) */
  fallback?: ReactNode
  children: ReactNode
}

/**
 * Conditionally renders children based on user permissions.
 * Unauthorized content is hidden (not rendered at all).
 *
 * @example
 * <PermissionGuard permission="equipment.create">
 *   <button>Add Equipment</button>
 * </PermissionGuard>
 *
 * @example
 * <PermissionGuard anyOf={["equipment.edit", "equipment.delete"]}>
 *   <ActionButtons />
 * </PermissionGuard>
 */
export function PermissionGuard({ permission, anyOf, allOf, fallback = null, children }: PermissionGuardProps) {
  const hasSingle = usePermission(permission || '')
  const hasAny = useHasAnyPermission(anyOf || [])

  // Determine access
  let hasAccess = true

  if (permission) {
    hasAccess = hasSingle
  } else if (anyOf && anyOf.length > 0) {
    hasAccess = hasAny
  } else if (allOf && allOf.length > 0) {
    hasAccess = useAuthStore.getState().hasAllPermissions(allOf)
  }

  if (!hasAccess) {
    return <>{fallback}</>
  }

  return <>{children}</>
}

interface PermissionRouteProps {
  /** Permission required to access this route */
  permission?: string
  /** Multiple permissions — user needs ANY of these */
  anyOf?: string[]
  /** Where to redirect when denied (defaults to /dashboard) */
  redirectTo?: string
  children: ReactNode
}

/**
 * Route-level permission guard that redirects when denied.
 *
 * @example
 * <PermissionRoute permission="settings.view">
 *   <SettingsPage />
 * </PermissionRoute>
 */
export function PermissionRoute({ permission, anyOf, redirectTo = '/dashboard', children }: PermissionRouteProps) {
  const hasSingle = usePermission(permission || '')
  const hasAny = useHasAnyPermission(anyOf || [])

  let hasAccess = true

  if (permission) {
    hasAccess = hasSingle
  } else if (anyOf && anyOf.length > 0) {
    hasAccess = hasAny
  }

  if (!hasAccess) {
    return <Navigate to={redirectTo} replace />
  }

  return <>{children}</>
}

export default PermissionGuard
