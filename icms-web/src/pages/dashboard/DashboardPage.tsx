import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import {
  Wrench,
  Users,
  Package,
  ClipboardList,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react'
import { dashboardService, type DashboardStats, type WorkOrderSummary } from '../../services/dashboard.service'
import type { InventoryItem } from '../../services/inventory.service'

const DashboardPage = () => {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentWorkOrders, setRecentWorkOrders] = useState<WorkOrderSummary[]>([])
  const [lowStockItems, setLowStockItems] = useState<InventoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setIsLoading(true)
      const [statsData, workOrders, lowStock] = await Promise.all([
        dashboardService.getAllStats(),
        dashboardService.getRecentWorkOrders(5),
        dashboardService.getLowStockItems(5),
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

  if (isLoading || !stats) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

  const statCards = [
    {
      title: 'Total Equipment',
      value: stats.equipment.total.toString(),
      subtitle: `${stats.equipment.operational} operational`,
      trend: 'up',
      icon: Wrench,
      color: 'blue',
    },
    {
      title: 'Active Craftsmen',
      value: stats.craftsmen.active.toString(),
      subtitle: `${stats.craftsmen.available} available`,
      trend: 'up',
      icon: Users,
      color: 'green',
    },
    {
      title: 'Inventory Items',
      value: stats.inventory.total_items.toString(),
      subtitle: `$${stats.inventory.total_value.toLocaleString()} total value`,
      trend: stats.inventory.low_stock_count > 5 ? 'down' : 'up',
      icon: Package,
      color: 'purple',
    },
    {
      title: 'Open Work Orders',
      value: (stats.workOrders.open + stats.workOrders.in_progress).toString(),
      subtitle: `${stats.workOrders.completed} completed`,
      trend: stats.workOrders.open > 10 ? 'up' : 'down',
      icon: ClipboardList,
      color: 'orange',
    },
  ]

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

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Here's what's happening in your facility today
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
              className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6 hover:shadow-md dark:hover:shadow-gray-900/70 transition-shadow"
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

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Work Orders */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Recent Work Orders</h2>
          </div>
          <div className="p-6">
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

        {/* Low Stock Alerts */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Low Stock Alerts</h2>
              <AlertTriangle className="w-5 h-5 text-orange-500 dark:text-orange-400" />
            </div>
          </div>
          <div className="p-6">
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
      </div>

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => navigate('/maintenance/work-orders/new')}
            className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary-500 dark:hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all group"
          >
            <ClipboardList className="w-6 h-6 text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">
              Create Work Order
            </span>
          </button>
          <button
            onClick={() => navigate('/inventory/new')}
            className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary-500 dark:hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all group"
          >
            <Package className="w-6 h-6 text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">
              Add Inventory Item
            </span>
          </button>
          <button
            onClick={() => navigate('/equipment/new')}
            className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary-500 dark:hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all group"
          >
            <Wrench className="w-6 h-6 text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">
              Register Equipment
            </span>
          </button>
          <button
            onClick={() => navigate('/maintenance/reports/new')}
            className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary-500 dark:hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all group"
          >
            <CheckCircle className="w-6 h-6 text-gray-400 dark:text-gray-500 group-hover:text-primary-600 dark:group-hover:text-primary-400 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400">
              Complete Maintenance
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
