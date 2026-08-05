import { create } from 'zustand'
import { companyService, type Company } from '../services/company.service'
import { useAuthStore } from './authStore'

interface CompanyState {
  company: Company | null
  isLoaded: boolean
  isLoading: boolean
  loadCompany: (force?: boolean) => Promise<void>
  setCompany: (company: Company) => void
}

export const useCompanyStore = create<CompanyState>()((set, get) => ({
  company: null,
  isLoaded: false,
  isLoading: false,

  loadCompany: async (force = false) => {
    const { isLoaded, isLoading } = get()
    if ((isLoaded && !force) || isLoading) return

    const { isAuthenticated, token } = useAuthStore.getState()
    if (!isAuthenticated || !token) return

    set({ isLoading: true })
    try {
      const company = await companyService.getCompany()
      set({ company, isLoaded: true, isLoading: false })
    } catch (error: any) {
      if (error?.response?.status !== 401) {
        console.error('Failed to load company:', error)
      }
      set({ company: null, isLoading: false })
    }
  },

  setCompany: (company) => set({ company, isLoaded: true }),
}))
