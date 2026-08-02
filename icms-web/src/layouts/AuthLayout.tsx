import { Outlet } from 'react-router-dom'

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">ICMS</h1>
          <p className="text-primary-100">Industry Computerized Management System</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-2xl p-8">
          <Outlet />
        </div>

        <div className="text-center mt-6 text-primary-100 text-sm">
          <p>&copy; {new Date().getFullYear()} ICMS. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
