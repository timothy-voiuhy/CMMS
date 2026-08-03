import apiClient from './apiClient'

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  phone?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UpdateUserRequest {
  email?: string
  full_name?: string
  phone?: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

class UserService {
  private baseUrl = '/api/v1/users'

  async getCurrentUser() {
    return apiClient.get<User>(`${this.baseUrl}/me`)
  }

  async getUserById(id: number) {
    return apiClient.get<User>(`${this.baseUrl}/${id}`)
  }

  async updateUser(id: number, data: UpdateUserRequest) {
    return apiClient.put<User>(`${this.baseUrl}/${id}`, data)
  }

  async changePassword(id: number, data: ChangePasswordRequest) {
    return apiClient.post(`${this.baseUrl}/${id}/change-password`, data)
  }

  async getUsers(params?: {
    skip?: number
    limit?: number
    search?: string
    role?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.skip) queryParams.append('skip', params.skip.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.search) queryParams.append('search', params.search)
    if (params?.role) queryParams.append('role', params.role)

    return apiClient.get<User[]>(`${this.baseUrl}?${queryParams.toString()}`)
  }
}

export const userService = new UserService()
