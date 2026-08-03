import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Theme = 'light' | 'dark' | 'system'

interface ThemeState {
  theme: Theme
  actualTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
}

const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const calculateActualTheme = (theme: Theme): 'light' | 'dark' => {
  if (theme === 'system') {
    return getSystemTheme()
  }
  return theme
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => {
      // Listen for system theme changes
      if (typeof window !== 'undefined') {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
          const currentTheme = get().theme
          if (currentTheme === 'system') {
            const newActualTheme = e.matches ? 'dark' : 'light'
            set({ actualTheme: newActualTheme })
            if (newActualTheme === 'dark') {
              document.documentElement.classList.add('dark')
            } else {
              document.documentElement.classList.remove('dark')
            }
          }
        })
      }

      return {
        theme: 'light',
        actualTheme: 'light',
        setTheme: (theme: Theme) => {
          const actualTheme = calculateActualTheme(theme)
          set({ theme, actualTheme })
          
          // Update document class for Tailwind dark mode
          if (typeof window !== 'undefined') {
            if (actualTheme === 'dark') {
              document.documentElement.classList.add('dark')
            } else {
              document.documentElement.classList.remove('dark')
            }
          }
        },
      }
    },
    {
      name: 'icms-theme-storage',
      onRehydrateStorage: () => (state) => {
        if (state) {
          const actualTheme = calculateActualTheme(state.theme)
          state.actualTheme = actualTheme
          if (typeof window !== 'undefined') {
            if (actualTheme === 'dark') {
              document.documentElement.classList.add('dark')
            } else {
              document.documentElement.classList.remove('dark')
            }
          }
        }
      },
    }
  )
)
