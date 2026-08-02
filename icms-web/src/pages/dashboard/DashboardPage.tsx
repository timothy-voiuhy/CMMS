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

const DashboardPage = () => {
  const { user } = useAuthStore()

  // Mock data - will be replaced with API calls
  const stats = [
    {
      title: 'Total Equipment',
      value: '156',
      change: '+12%',
      trend: 'up',
      icon: Wrench,
      color: 'blue',
    },
    {
      title: 'Active Craftsmen',
      value: '48',
      change: '+3',
      trend: 'up',
      icon: Users,
      color: 'green',
    },
    {
      title: 'Inventory Items',
      value: '1,234',
      change: '-5%',
      trend: 'down',
      icon: Package,
      color: 'purple',
    },
    {
      title: 'Open Work Orders',
      value: '23',
      change: '-8',
      trend: 'down',
      icon: ClipboardList,
      color: 'orange',
    },
  ]

  const recentWorkOrders = [
    { id: 'WO-001', title: 'Hydraulic Press Maintenance', status: 'In Progress', priority: 'High' },
    { id: 'WO-002', title: 'CNC Machine Calibration', status: 'Open', priority: 'Medium' },
    { id: 'WO-003', title: 'Conveyor Belt Repair', status: 'Completed', priority: 'Low' },
  ]

  const lowStockItems = [
    { code: 'BRG-001', name: 'Ball Bearing 6205', quantity: 5, reorderPoint: 10 },
    { code: 'FLT-023', name: 'Oil Filter', quantity: 3, reorderPoint: 8 },
    { code: 'BLT-045', name: 'V-Belt A-42', quantity: 2, reorderPoint: 5 },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">
          Welcome back, {user?.firstName}!
        </h1>
        <p className="text-gray-600 mt-1">
          Here's what's happening in your facility today
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          const colorClasses = {
            blue: 'bg-blue-100 text-blue-600',
            green: 'bg-green-100 text-green-600',
            purple: 'bg-purple-100 text-purple-600',
            orange: 'bg-orange-100 text-orange-600',
          }

          return (
            <div
              key={stat.title}
              className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${colorClasses[stat.color as keyof typeof colorClasses]}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex items-center space-x-1 text-sm">
                  {stat.trend === 'up' ? (
                    <>
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      <span className="text-green-600 font-medium">{stat.change}</span>
                    </>
                  ) : (
                    <>
                      <TrendingDown className="w-4 h-4 text-red-500" />
                      <span className="text-red-600 font-medium">{stat.change}</span>
                    </>
                  )}
                </div>
              </div>
              <h3 className="text-gray-600 text-sm font-medium">{stat.title}</h3>
              <p className="text-3xl font-bold text-gray-800 mt-1">{stat.value}</p>
            </div>
          )
        })}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Work Orders */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">Recent Work Orders</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentWorkOrders.map((wo) => (
                <div key={wo.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-800">{wo.id}</span>
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded ${
                          wo.priority === 'High'
                            ? 'bg-red-100 text-red-700'
                            : wo.priority === 'Medium'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}
                      >
                        {wo.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{wo.title}</p>
                  </div>
                  <span
                    className={`px-3 py-1 text-xs font-medium rounded-full ${
                      wo.status === 'Completed'
                        ? 'bg-green-100 text-green-700'
                        : wo.status === 'In Progress'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {wo.status}
                  </span>
                </div>
              ))}
            </div>
            <button className="w-full mt-4 py-2 text-sm text-primary-600 hover:text-primary-700 font-medium">
              View all work orders →
            </button>
          </div>
        </div>

        {/* Low Stock Alerts */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">Low Stock Alerts</h2>
              <AlertTriangle className="w-5 h-5 text-orange-500" />
            </div>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {lowStockItems.map((item) => (
                <div key={item.code} className="flex items-center justify-between p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-800">{item.code}</span>
                      <span className="text-xs text-gray-500">({item.name})</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-xs text-gray-600">
                        Stock: <span className="font-semibold text-orange-600">{item.quantity}</span>
                      </span>
                      <span className="text-xs text-gray-400">|</span>
                      <span className="text-xs text-gray-600">
                        Reorder: {item.reorderPoint}
                      </span>
                    </div>
                  </div>
                  <button className="px-3 py-1 bg-orange-600 text-white text-xs font-medium rounded hover:bg-orange-700 transition-colors">
                    Reorder
                  </button>
                </div>
              ))}
            </div>
            <button className="w-full mt-4 py-2 text-sm text-primary-600 hover:text-primary-700 font-medium">
              View inventory →
            </button>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all group">
            <ClipboardList className="w-6 h-6 text-gray-400 group-hover:text-primary-600 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-600 group-hover:text-primary-600">
              Create Work Order
            </span>
          </button>
          <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all group">
            <Package className="w-6 h-6 text-gray-400 group-hover:text-primary-600 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-600 group-hover:text-primary-600">
              Add Inventory Item
            </span>
          </button>
          <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all group">
            <Wrench className="w-6 h-6 text-gray-400 group-hover:text-primary-600 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-600 group-hover:text-primary-600">
              Register Equipment
            </span>
          </button>
          <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all group">
            <CheckCircle className="w-6 h-6 text-gray-400 group-hover:text-primary-600 mx-auto mb-2" />
            <span className="text-sm font-medium text-gray-600 group-hover:text-primary-600">
              Complete Maintenance
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
