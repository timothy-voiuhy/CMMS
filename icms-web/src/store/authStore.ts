import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  username: string
  full_name: string
  email: string
  role: 'admin' | 'craftsman' | 'inventory' | 'production' | 'quality' | 'manager' | 'readonly'
  phone?: string
  is_active: boolean
  created_at: string
  updated_at: string
  permissions?: string[]
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (user: User, token: string, refreshToken?: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
  setPermissions: (permissions: string[]) => void
  hasPermission: (permission: string) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      
      login: (user, token, refreshToken) => {
        set({
          user,
          token,
          refreshToken,
          isAuthenticated: true,
        })
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },
      
      updateUser: (userData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        }))
      },

      setPermissions: (permissions: string[]) => {
        set((state) => ({
          user: state.user ? { ...state.user, permissions } : null,
        }))
      },

      hasPermission: (permission: string): boolean => {
        const { user } = get()
        if (!user) return false
        // Admin users have full access
        if (user.role === 'admin') return true
        const perms = user.permissions || []
        return perms.includes(permission) || perms.includes('*') || perms.includes('admin.full_access')
      },

      hasAnyPermission: (permissions: string[]): boolean => {
        const { hasPermission } = get()
        return permissions.some((p) => hasPermission(p))
      },

      hasAllPermissions: (permissions: string[]): boolean => {
        const { hasPermission } = get()
        return permissions.every((p) => hasPermission(p))
      },
    }),
    {
      name: 'icms-auth-storage',
    }
  )
)
