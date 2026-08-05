import apiClient from './apiClient'

// ==================== COMPANY TYPES ====================

export interface Company {
  id: number
  name: string
  short_name?: string
  industry_type?: string
  registration_number?: string
  tax_id?: string
  address?: string
  city?: string
  country?: string
  phone?: string
  email?: string
  website?: string
  currency: string
  timezone: string
  language: string
  working_hours_start?: string
  working_hours_end?: string
  working_days?: string
  logo_url?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateCompanyRequest {
  name: string
  short_name?: string
  industry_type?: string
  registration_number?: string
  tax_id?: string
  address?: string
  city?: string
  country?: string
  phone?: string
  email?: string
  website?: string
  currency?: string
  timezone?: string
  language?: string
  working_hours_start?: string
  working_hours_end?: string
  working_days?: string
  logo_url?: string
  is_active?: boolean
}

export interface UpdateCompanyRequest {
  name?: string
  short_name?: string
  industry_type?: string
  registration_number?: string
  tax_id?: string
  address?: string
  city?: string
  country?: string
  phone?: string
  email?: string
  website?: string
  currency?: string
  timezone?: string
  language?: string
  working_hours_start?: string
  working_hours_end?: string
  working_days?: string
  logo_url?: string
  is_active?: boolean
}

// ==================== FACILITY TYPES ====================

export interface Facility {
  id: number
  company_id: number
  name: string
  facility_type: string
  facility_code: string
  address?: string
  city?: string
  country?: string
  gps_coordinates?: string
  phone?: string
  manager_name?: string
  manager_contact?: string
  is_active: boolean
  notes?: string
  created_at: string
  updated_at: string
}

export interface CreateFacilityRequest {
  company_id: number
  name: string
  facility_type: string
  facility_code: string
  address?: string
  city?: string
  country?: string
  gps_coordinates?: string
  phone?: string
  manager_name?: string
  manager_contact?: string
  is_active?: boolean
  notes?: string
}

export interface UpdateFacilityRequest {
  name?: string
  facility_type?: string
  facility_code?: string
  address?: string
  city?: string
  country?: string
  gps_coordinates?: string
  phone?: string
  manager_name?: string
  manager_contact?: string
  is_active?: boolean
  notes?: string
}

// ==================== DEPARTMENT TYPES ====================

export interface Department {
  id: number
  facility_id: number
  name: string
  department_code: string
  description?: string
  manager_name?: string
  cost_center?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateDepartmentRequest {
  facility_id: number
  name: string
  department_code: string
  description?: string
  manager_name?: string
  cost_center?: string
  is_active?: boolean
}

export interface UpdateDepartmentRequest {
  name?: string
  department_code?: string
  description?: string
  manager_name?: string
  cost_center?: string
  is_active?: boolean
}

// ==================== ROLE TYPES ====================

export interface Role {
  id: number
  name: string
  description?: string
  level: number
  category?: string
  permissions_json?: string
  is_active: boolean
  is_system_role: boolean
  created_at: string
  updated_at: string
}

export interface CreateRoleRequest {
  name: string
  description?: string
  level?: number
  category?: string
  permissions_json?: string
  is_active?: boolean
  is_system_role?: boolean
}

export interface UpdateRoleRequest {
  name?: string
  description?: string
  level?: number
  category?: string
  permissions_json?: string
  is_active?: boolean
  is_system_role?: boolean
}

class CompanyService {
  private baseUrl = '/api/v1/company'
  private rootUrl = '/api/v1/company/'

  // ==================== COMPANY METHODS ====================

  async getCompany() {
    return apiClient.get<Company>(this.rootUrl)
  }

  async createCompany(data: CreateCompanyRequest) {
    return apiClient.post<Company>(this.rootUrl, data)
  }

  async updateCompany(id: number, data: UpdateCompanyRequest) {
    return apiClient.put<Company>(`${this.baseUrl}/${id}`, data)
  }

  // ==================== FACILITY METHODS ====================

  async getFacilities(companyId?: number) {
    const params = new URLSearchParams()
    if (companyId) params.append('company_id', companyId.toString())
    return apiClient.get<Facility[]>(`${this.baseUrl}/facilities?${params.toString()}`)
  }

  async getFacilityById(id: number) {
    return apiClient.get<Facility>(`${this.baseUrl}/facilities/${id}`)
  }

  async createFacility(data: CreateFacilityRequest) {
    return apiClient.post<Facility>(`${this.baseUrl}/facilities`, data)
  }

  async updateFacility(id: number, data: UpdateFacilityRequest) {
    return apiClient.put<Facility>(`${this.baseUrl}/facilities/${id}`, data)
  }

  async deleteFacility(id: number) {
    return apiClient.delete(`${this.baseUrl}/facilities/${id}`)
  }

  // ==================== DEPARTMENT METHODS ====================

  async getDepartments(facilityId?: number) {
    const params = new URLSearchParams()
    if (facilityId) params.append('facility_id', facilityId.toString())
    return apiClient.get<Department[]>(`${this.baseUrl}/departments?${params.toString()}`)
  }

  async getDepartmentById(id: number) {
    return apiClient.get<Department>(`${this.baseUrl}/departments/${id}`)
  }

  async createDepartment(data: CreateDepartmentRequest) {
    return apiClient.post<Department>(`${this.baseUrl}/departments`, data)
  }

  async updateDepartment(id: number, data: UpdateDepartmentRequest) {
    return apiClient.put<Department>(`${this.baseUrl}/departments/${id}`, data)
  }

  async deleteDepartment(id: number) {
    return apiClient.delete(`${this.baseUrl}/departments/${id}`)
  }

  // ==================== ROLE METHODS ====================

  async getRoles(activeOnly?: boolean) {
    const params = new URLSearchParams()
    if (activeOnly) params.append('active_only', 'true')
    return apiClient.get<Role[]>(`${this.baseUrl}/roles?${params.toString()}`)
  }

  async getRoleById(id: number) {
    return apiClient.get<Role>(`${this.baseUrl}/roles/${id}`)
  }

  async createRole(data: CreateRoleRequest) {
    return apiClient.post<Role>(`${this.baseUrl}/roles`, data)
  }

  async updateRole(id: number, data: UpdateRoleRequest) {
    return apiClient.put<Role>(`${this.baseUrl}/roles/${id}`, data)
  }

  async deleteRole(id: number) {
    return apiClient.delete(`${this.baseUrl}/roles/${id}`)
  }
}

export const companyService = new CompanyService()
