import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore, type User as AuthStoreUser } from '../../store/authStore'
import { authService } from '../../services/auth.service'
import { LogIn, Eye, EyeOff, Users } from 'lucide-react'

const toAuthStoreRole = (role?: string): AuthStoreUser['role'] => {
  const normalized = (role || 'readonly').toLowerCase()
  const allowedRoles: AuthStoreUser['role'][] = ['admin', 'craftsman', 'inventory', 'production', 'quality', 'manager', 'readonly']
  return allowedRoles.includes(normalized as AuthStoreUser['role'])
    ? normalized as AuthStoreUser['role']
    : 'readonly'
}

const LoginPage = () => {
  const navigate = useNavigate()
  const { login, logout } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    rememberMe: false,
  })

  useEffect(() => {
    const checkSetup = async () => {
      try {
        const res = await authService.checkSetupStatus()
        if (res.setup_required) {
          navigate('/setup', { replace: true })
        }
      } catch (err) {
        console.error('Error checking setup status:', err)
      }
    }
    checkSetup()
  }, [navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Call real backend API
      const response = await authService.login({
        username: formData.username,
        password: formData.password,
      })

      console.log('Login successful, access token received')

      // Store token temporarily to make authenticated /me request
      const tempStore = useAuthStore.getState()
      
      // Create a temporary user object just to set the token
      const tempUser = {
        id: '0',
        username: formData.username,
        full_name: '',
        email: '',
        role: 'readonly' as const,
        is_active: true,
        created_at: '',
        updated_at: '',
        permissions: [],
      }
      
      // Set token first
      tempStore.login(tempUser, response.access_token, response.refresh_token)
      
      // Now get user info with the token in place (includes resolved permissions)
      const user = await authService.getCurrentUser()

      // Now set the real user data with the token and permissions
      login(
        {
          id: user.id.toString(),
          username: user.username,
          full_name: user.full_name,
          email: user.email,
          role: toAuthStoreRole(user.role),
          is_active: user.is_active,
          phone: user.phone,
          created_at: user.created_at || '',
          updated_at: user.updated_at || '',
          permissions: user.permissions || [],
        },
        response.access_token,
        response.refresh_token
      )

      navigate('/dashboard')
    } catch (err: unknown) {
      console.error('Login error:', err)
      logout()
      
      // Handle validation errors (422) which return an array
      let errorMessage = 'Invalid username or password'
      
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const response = (err as { response?: { data?: { detail?: unknown }; status?: number; statusText?: string } }).response
        const detail = response?.data?.detail
        if (detail) {
          if (Array.isArray(detail)) {
            // Format validation errors
            errorMessage = detail.map((e: { msg?: string; message?: string }) => e.msg || e.message).join(', ')
          } else if (typeof detail === 'string') {
            errorMessage = detail
          }
        }
      } else if (err instanceof Error) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
      
      // Log full error details to console so you can see them
      console.error('Full error details:', {
        status: typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response?: { status?: number } }).response?.status
          : undefined,
        statusText: typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response?: { statusText?: string } }).response?.statusText
          : undefined,
        data: typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response?: { data?: unknown } }).response?.data
          : undefined,
        message: err instanceof Error ? err.message : undefined,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-800">Welcome Back</h2>
        <p className="text-gray-600 mt-2">Sign in to your account to continue</p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <input
            id="username"
            type="text"
            required
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your username"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 transition-colors"
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.rememberMe}
              onChange={(e) => setFormData({ ...formData, rememberMe: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-600">Remember me</span>
          </label>

          <button
            type="button"
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Forgot password?
          </button>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-colors"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Signing in...</span>
            </>
          ) : (
            <>
              <LogIn className="w-5 h-5" />
              <span>Sign In</span>
            </>
          )}
        </button>
      </form>

      <div className="mt-6 text-center">
        <Link
          to="/dev/role-testing"
          className="inline-flex items-center justify-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          <Users className="h-4 w-4" />
          Open development role tester
        </Link>
      </div>

      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">
          Need help?{' '}
          <button type="button" className="text-blue-600 hover:text-blue-700 font-medium">
            Contact support
          </button>
        </p>
      </div>
    </div>
  )
}

export default LoginPage
