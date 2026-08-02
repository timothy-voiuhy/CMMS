import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, Search, Menu, LogOut, User, Settings } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

interface HeaderProps {
  onMenuClick: () => void
}

const Header = ({ onMenuClick }: HeaderProps) => {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      {/* Left Section */}
      <div className="flex items-center space-x-4 flex-1">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
        >
          <Menu className="w-5 h-5 text-gray-600" />
        </button>

        {/* Search Bar */}
        <div className="hidden md:flex items-center flex-1 max-w-lg">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search equipment, work orders, craftsmen..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-lg hover:bg-gray-100 relative"
          >
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
              <div className="p-4 border-b border-gray-200">
                <h3 className="font-semibold text-gray-800">Notifications</h3>
              </div>
              <div className="max-h-96 overflow-y-auto">
                <div className="p-4 hover:bg-gray-50 border-b border-gray-100 cursor-pointer">
                  <p className="text-sm font-medium text-gray-800">New work order assigned</p>
                  <p className="text-xs text-gray-500 mt-1">WO-2024-001 requires your attention</p>
                  <p className="text-xs text-gray-400 mt-1">2 hours ago</p>
                </div>
                <div className="p-4 hover:bg-gray-50 border-b border-gray-100 cursor-pointer">
                  <p className="text-sm font-medium text-gray-800">Low stock alert</p>
                  <p className="text-xs text-gray-500 mt-1">Item BRG-001 below reorder point</p>
                  <p className="text-xs text-gray-400 mt-1">5 hours ago</p>
                </div>
                <div className="p-4 hover:bg-gray-50 cursor-pointer">
                  <p className="text-sm font-medium text-gray-800">Maintenance due</p>
                  <p className="text-xs text-gray-500 mt-1">Equipment EQ-125 scheduled maintenance</p>
                  <p className="text-xs text-gray-400 mt-1">1 day ago</p>
                </div>
              </div>
              <div className="p-3 border-t border-gray-200 text-center">
                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                  View all notifications
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100"
          >
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <span className="text-primary-600 font-semibold text-sm">
                {user?.firstName[0]}{user?.lastName[0]}
              </span>
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium text-gray-800">
                {user?.firstName} {user?.lastName}
              </p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
          </button>

          {/* User Dropdown */}
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
              <div className="py-2">
                <button
                  onClick={() => {
                    navigate('/settings/profile')
                    setShowUserMenu(false)
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                >
                  <User className="w-4 h-4" />
                  <span>Profile</span>
                </button>
                <button
                  onClick={() => {
                    navigate('/settings')
                    setShowUserMenu(false)
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                >
                  <Settings className="w-4 h-4" />
                  <span>Settings</span>
                </button>
                <hr className="my-2" />
                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
