import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  employeeId: string
  firstName: string
  lastName: string
  email: string
  role: 'admin' | 'craftsman' | 'inventory' | 'production' | 'quality' | 'manager'
  accessLevel?: string
  permissions: string[]
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (user: User, token: string, refreshToken?: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
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
    }),
    {
      name: 'icms-auth-storage',
    }
  )
)
