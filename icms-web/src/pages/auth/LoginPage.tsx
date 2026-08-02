import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { authService } from '../../services/auth.service'
import { LogIn } from 'lucide-react'

const LoginPage = () => {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    rememberMe: false,
  })

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
        employeeId: formData.username,
        firstName: '',
        lastName: '',
        email: '',
        role: 'admin' as const,
        permissions: [],
      }
      
      // Set token first
      tempStore.login(tempUser, response.access_token, response.refresh_token)
      
      // Now get user info with the token in place
      const user = await authService.getCurrentUser()

      // Now set the real user data with the token
      login(
        {
          id: user.id.toString(),
          employeeId: user.username,
          firstName: user.full_name.split(' ')[0] || user.username,
          lastName: user.full_name.split(' ')[1] || '',
          email: user.email,
          role: user.role as any,
          permissions: ['all'], // TODO: Get from backend
        },
        response.access_token,
        response.refresh_token
      )

      navigate('/dashboard')
    } catch (err: any) {
      console.error('Login error:', err)
      
      // Handle validation errors (422) which return an array
      let errorMessage = 'Invalid username or password'
      
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        if (Array.isArray(detail)) {
          // Format validation errors
          errorMessage = detail.map((e: any) => e.msg || e.message).join(', ')
        } else if (typeof detail === 'string') {
          errorMessage = detail
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
      
      // Log full error details to console so you can see them
      console.error('Full error details:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        message: err.message,
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
          <input
            id="password"
            type="password"
            required
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your password"
          />
        </div>

        <div className="flex items-center justify-between">
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
