import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { useCompanyStore } from '../../store/companyStore'
import { usePermission } from '../../hooks/usePermission'
import {
  Wrench,
  Users,
  Package,
  ClipboardList,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  ShieldAlert,
  Building,
  MapPin,
  Calendar,
} from 'lucide-react'
import { dashboardService, type DashboardStats, type WorkOrderSummary } from '../../services/dashboard.service'
import type { InventoryItem } from '../../services/inventory.service'

const DashboardPage = () => {
  const { user } = useAuthStore()
  const { company, loadCompany } = useCompanyStore()
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentWorkOrders, setRecentWorkOrders] = useState<WorkOrderSummary[]>([])
  const [lowStockItems, setLowStockItems] = useState<InventoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Permission checks for each dashboard section
  const canViewEquipment = usePermission('equipment.view')
  const canViewCraftsmen = usePermission('craftsmen.view')
  const canViewInventory = usePermission('inventory.view')
  const canViewWorkOrders = usePermission('work_orders.view')
  const canViewMaintenance = usePermission('maintenance.view')
  const canCreateWorkOrders = usePermission('work_orders.create')
  const canCreateInventory = usePermission('inventory.create')
  const canCreateEquipment = usePermission('equipment.create')
  const canCreateMaintenance = usePermission('maintenance.create')

  // Check if user has any dashboard-relevant permissions at all
  const hasAnyPermission = canViewEquipment || canViewCraftsmen || canViewInventory || canViewWorkOrders || canViewMaintenance

  useEffect(() => {
    loadCompany()
    if (hasAnyPermission) {
      loadDashboardData()
    } else {
      setIsLoading(false)
    }
  }, [hasAnyPermission, loadCompany])

  const loadDashboardData = async () => {
    try {
      setIsLoading(true)
      const [statsData, workOrders, lowStock] = await Promise.all([
        dashboardService.getAllStats(),
        canViewWorkOrders ? dashboardService.getRecentWorkOrders(5) : Promise.resolve([]),
        canViewInventory ? dashboardService.getLowStockItems(5) : Promise.resolve([]),
      ])
      setStats(statsData)
      setRecentWorkOrders(workOrders)
      setLowStockItems(lowStock)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const today = new Date()
  const greeting = today.getHours() < 12 ? 'Good morning' : today.getHours() < 17 ? 'Good afternoon' : 'Good evening'
  const formattedDate = today.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

  // Build stat cards based on permissions (after loading check)
  const statCards: Array<{ title: string; value: string; subtitle: string; trend: string; icon: any; color: string }> = []

  if (!isLoading && stats) {
    if (canViewEquipment) {
      statCards.push({
        title: 'Total Equipment',
        value: stats.equipment.total.toString(),
        subtitle: `${stats.equipment.operational} operational`,
        trend: 'up',
        icon: Wrench,
        color: 'blue',
      })
    }

    if (canViewCraftsmen) {
      statCards.push({
        title: 'Active Craftsmen',
        value: stats.craftsmen.active.toString(),
        subtitle: `${stats.craftsmen.available} available`,
        trend: 'up',
        icon: Users,
        color: 'green',
      })
    }

    if (canViewInventory) {
      statCards.push({
        title: 'Inventory Items',
        value: stats.inventory.total_items.toString(),
        subtitle: `$${stats.inventory.total_value.toLocaleString()} total value`,
        trend: stats.inventory.low_stock_count > 5 ? 'down' : 'up',
        icon: Package,
        color: 'purple',
      })
    }

    if (canViewWorkOrders) {
      statCards.push({
        title: 'Open Work Orders',
        value: (stats.workOrders.open + stats.workOrders.in_progress).toString(),
        subtitle: `${stats.workOrders.completed} completed`,
        trend: stats.workOrders.open > 10 ? 'up' : 'down',
        icon: ClipboardList,
        color: 'orange',
      })
    }
  }

  // Build quick actions based on permissions
  const quickActions: Array<{ label: string; icon: any; path: string }> = []

  if (canCreateWorkOrders) {
    quickActions.push({
      label: 'Create Work Order',
      icon: ClipboardList,
      path: '/maintenance/work-orders/new',
    })
  }

  if (canCreateInventory) {
    quickActions.push({
      label: 'Add Inventory Item',
      icon: Package,
      path: '/inventory/new',
    })
  }

  if (canCreateEquipment) {
    quickActions.push({
      label: 'Register Equipment',
      icon: Wrench,
      path: '/equipment/new',
    })
  }

  if (canCreateMaintenance) {
    quickActions.push({
      label: 'Complete Maintenance',
      icon: CheckCircle,
      path: '/maintenance/reports/new',
    })
  }

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase()
    if (statusLower.includes('completed')) return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
    if (statusLower.includes('progress')) return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
    if (statusLower.includes('cancelled')) return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
    return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
  }

  const getPriorityColor = (priority: string) => {
    const priorityLower = priority.toLowerCase()
    if (priorityLower === 'high' || priorityLower === 'urgent') return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
    if (priorityLower === 'medium') return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
    return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Welcome Banner */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 sm:p-6 shadow dark:shadow-gray-900/50 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              {greeting}, {user?.full_name?.split(' ')[0] || 'User'}!
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              {hasAnyPermission
                ? "Here's what's happening in your facility today"
                : 'Your account is active but you have no assigned permissions yet'}
            </p>
          </div>
          <div className="flex flex-col sm:flex-row sm:flex-wrap gap-2 sm:gap-4 text-sm text-gray-500 dark:text-gray-400">
            {company && (
              <>
                <span className="flex items-center gap-1.5">
                  <Building className="w-4 h-4 text-gray-400 dark:text-gray-500" />
                  {company.name}
                </span>
                {(company.city || company.country) && (
                  <span className="flex items-center gap-1.5">
                    <MapPin className="w-4 h-4 text-gray-400 dark:text-gray-500" />
                    {[company.city, company.country].filter(Boolean).join(', ')}
                  </span>
                )}
              </>
            )}
            <span className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-gray-400 dark:text-gray-500" />
              {formattedDate}
            </span>
          </div>
        </div>
      </div>

      {/* No Permissions State */}
      {!hasAnyPermission && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-12 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-amber-100 dark:bg-amber-900/30 rounded-full">
              <ShieldAlert className="w-10 h-10 text-amber-600 dark:text-amber-400" />
            </div>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
            No Permissions Assigned
          </h2>
          <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
            Your account doesn't have any role or permissions assigned yet. Please contact your System Administrator to get your role configured.
          </p>
        </div>
      )}

      {/* Stats Grid — only show if there are visible cards */}
      {statCards.length > 0 && (
        <div className={`grid grid-cols-2 md:grid-cols-2 lg:grid-cols-${Math.min(statCards.length, 4)} gap-3 sm:gap-6`}>
          {statCards.map((stat) => {
            const Icon = stat.icon
            const colorClasses = {
              blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
              green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
              purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
              orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
            }

            return (
              <div
                key={stat.title}
                className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-4 sm:p-6 hover:shadow-md dark:hover:shadow-gray-900/70 transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg ${colorClasses[stat.color as keyof typeof colorClasses]}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex items-center space-x-1 text-sm">
                    {stat.trend === 'up' ? (
                      <TrendingUp className="w-4 h-4 text-green-500 dark:text-green-400" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-500 dark:text-red-400" />
                    )}
                  </div>
                </div>
                <h3 className="text-gray-600 dark:text-gray-400 text-sm font-medium">{stat.title}</h3>
                <p className="text-3xl font-bold text-gray-800 dark:text-gray-100 mt-1">{stat.value}</p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{stat.subtitle}</p>
              </div>
            )
          })}
        </div>
      )}

      {/* Content Grid — only if user can see work orders or inventory */}
      {(canViewWorkOrders || canViewInventory) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Work Orders */}
          {canViewWorkOrders && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50">
              <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Recent Work Orders</h2>
              </div>
              <div className="p-4 sm:p-6">
                <div className="space-y-4">
                  {recentWorkOrders.length === 0 ? (
                    <p className="text-center text-gray-500 dark:text-gray-400 py-8">No work orders found</p>
                  ) : (
                    recentWorkOrders.map((wo) => (
                      <div
                        key={wo.id}
                        className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        onClick={() => navigate(`/maintenance/work-orders/${wo.id}`)}
                      >
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{wo.order_number}</span>
                            <span className={`px-2 py-0.5 text-xs font-medium rounded ${getPriorityColor(wo.priority)}`}>
                              {wo.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{wo.title}</p>
                        </div>
                        <span className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(wo.status)}`}>
                          {wo.status}
                        </span>
                      </div>
                    ))
                  )}
                </div>
                <button
                  onClick={() => navigate('/maintenance/work-orders')}
                  className="w-full mt-4 py-2 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
                >
                  View all work orders →
                </button>
              </div>
            </div>
          )}

          {/* Low Stock Alerts */}
          {canViewInventory && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50">
              <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Low Stock Alerts</h2>
                  <AlertTriangle className="w-5 h-5 text-orange-500 dark:text-orange-400" />
                </div>
              </div>
              <div className="p-4 sm:p-6">
                <div className="space-y-4">
                  {lowStockItems.length === 0 ? (
                    <p className="text-center text-gray-500 dark:text-gray-400 py-8">No low stock items</p>
                  ) : (
                    lowStockItems.map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800"
                      >
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{item.item_code}</span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">({item.name})</span>
                          </div>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className="text-xs text-gray-600 dark:text-gray-400">
                              Stock: <span className="font-semibold text-orange-600 dark:text-orange-400">{item.quantity}</span>
                            </span>
                            <span className="text-xs text-gray-400 dark:text-gray-600">|</span>
                            <span className="text-xs text-gray-600 dark:text-gray-400">
                              Reorder: {item.reorder_point || 'N/A'}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => navigate(`/inventory/${item.id}`)}
                          className="px-3 py-1 bg-orange-600 dark:bg-orange-500 text-white text-xs font-medium rounded hover:bg-orange-700 dark:hover:bg-orange-600 transition-colors"
                        >
                          View
                        </button>
                      </div>
                    ))
                  )}
                </div>
                <button
                  onClick={() => navigate('/inventory')}
                  className="w-full mt-4 py-2 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
                >
                  View inventory →
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Quick Actions — only show actions the user has permission for */}
      {quickActions.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Quick Actions</h2>
          <div className={`grid grid-cols-2 md:grid-cols-${Math.min(quickActions.length, 4)} gap-4`}>
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <button
                  key={action.path}
                  onClick={() => navigate(action.path)}
                  className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary-500 dark:hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all group"
                >
                  <Icon className="w-6 h-6 text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 mx-auto mb-2" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">
                    {action.label}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage
