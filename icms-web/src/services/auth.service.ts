import { apiClient } from './apiClient'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  phone?: string
}

export interface RefreshTokenResponse {
  access_token: string
  token_type: string
}

export const authService = {
  /**
   * Login user
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    return apiClient.post<LoginResponse>('/api/v1/auth/login', formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/api/v1/auth/me')
  },

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<RefreshTokenResponse> {
    return apiClient.post<RefreshTokenResponse>('/api/v1/auth/refresh')
  },

  /**
   * Logout (optional - mainly client-side token removal)
   */
  logout(): void {
    // Clear tokens from storage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}

export default authService
