import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Wrench,
  Users,
  Package,
  ClipboardList,
  History,
  Factory,
  PackageCheck,
  ShieldCheck,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronDown,
  FileText,
  UserCog,
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useState } from 'react'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

interface NavItem {
  path: string
  icon: any
  label: string
  roles?: string[]
  children?: NavItem[]
}

const navItems: NavItem[] = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/equipment', icon: Wrench, label: 'Equipment' },
  { path: '/craftsmen', icon: Users, label: 'Craftsmen' },
  { path: '/inventory', icon: Package, label: 'Inventory' },
  {
    path: '/maintenance',
    icon: History,
    label: 'Maintenance',
    children: [
      { path: '/maintenance/work-orders', icon: ClipboardList, label: 'Work Orders' },
      { path: '/maintenance/reports', icon: FileText, label: 'Reports' },
      { path: '/maintenance/personnel', icon: UserCog, label: 'Personnel' },
    ],
  },
  {
    path: '/production',
    icon: Factory,
    label: 'Production',
    children: [
      { path: '/production/lines', icon: Factory, label: 'Production Lines' },
      { path: '/production/orders', icon: ClipboardList, label: 'Production Orders' },
      { path: '/production/packaging', icon: PackageCheck, label: 'Packaging' },
    ],
  },
  { path: '/quality', icon: ShieldCheck, label: 'Quality' },
  { path: '/reports', icon: BarChart3, label: 'Reports' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

const Sidebar = ({ isOpen, onToggle }: SidebarProps) => {
  const { user } = useAuthStore()
  const [expandedItems, setExpandedItems] = useState<string[]>(['/maintenance', '/production'])

  const toggleExpanded = (path: string) => {
    setExpandedItems((prev) =>
      prev.includes(path) ? prev.filter((p) => p !== path) : [...prev, path]
    )
  }

  return (
    <>
      {/* Sidebar */}
      <aside
        className={`${
          isOpen ? 'w-64' : 'w-20'
        } bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ease-in-out flex flex-col`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
          {isOpen && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-500 dark:bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">IC</span>
              </div>
              <span className="font-bold text-gray-800 dark:text-gray-100">ICMS</span>
            </div>
          )}
          <button
            onClick={onToggle}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <ChevronLeft
              className={`w-5 h-5 text-gray-600 dark:text-gray-400 transition-transform ${
                !isOpen && 'rotate-180'
              }`}
            />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-3">
            {navItems.map((item) => (
              <li key={item.path}>
                {item.children ? (
                  // Parent with children
                  <div>
                    <button
                      onClick={() => {
                        if (isOpen) {
                          toggleExpanded(item.path)
                        }
                      }}
                      className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100 transition-all"
                    >
                      <div className="flex items-center space-x-3">
                        <item.icon className="w-5 h-5 flex-shrink-0" />
                        {isOpen && <span className="font-medium">{item.label}</span>}
                      </div>
                      {isOpen && (
                        <ChevronDown
                          className={`w-4 h-4 transition-transform ${
                            expandedItems.includes(item.path) ? 'rotate-180' : ''
                          }`}
                        />
                      )}
                    </button>
                    {/* Sub-menu */}
                    {isOpen && expandedItems.includes(item.path) && (
                      <ul className="mt-1 space-y-1 ml-4">
                        {item.children.map((child) => (
                          <li key={child.path}>
                            <NavLink
                              to={child.path}
                              className={({ isActive }) =>
                                `flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition-all ${
                                  isActive
                                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
                                }`
                              }
                            >
                              <child.icon className="w-4 h-4 flex-shrink-0" />
                              <span className="font-medium">{child.label}</span>
                            </NavLink>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ) : (
                  // Regular item
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all ${
                        isActive
                          ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
                      }`
                    }
                  >
                    <item.icon className="w-5 h-5 flex-shrink-0" />
                    {isOpen && <span className="font-medium">{item.label}</span>}
                  </NavLink>
                )}
              </li>
            ))}
          </ul>
        </nav>

        {/* User Info */}
        {isOpen && user && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <span className="text-primary-600 dark:text-primary-400 font-semibold">
                  {user.full_name?.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {user.full_name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate capitalize">{user.role}</p>
              </div>
            </div>
          </div>
        )}
      </aside>
    </>
  )
}

export default Sidebar
