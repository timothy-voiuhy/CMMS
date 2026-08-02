import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus,
  ClipboardList,
  Clock,
  PlayCircle,
  PauseCircle,
  CheckCircle,
  XCircle,
  Search,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
  TrendingUp,
} from 'lucide-react'
import {
  productionOrderService,
  type ProductionOrder,
  type ProductionOrderStatistics,
  type ProductionOrderStatus,
} from '../../services/production.service'

const ProductionOrdersPage: React.FC = () => {
  const navigate = useNavigate()
  const [orders, setOrders] = useState<ProductionOrder[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [statistics, setStatistics] = useState<ProductionOrderStatistics | null>(null)
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    search: '',
    status: '' as ProductionOrderStatus | '',
  })
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    loadOrders()
    loadStatistics()
  }, [filters])

  const loadOrders = async () => {
    try {
      setIsLoading(true)
      const response = await productionOrderService.getAll(filters)
      setOrders(response.data)
      setTotalPages(response.totalPages)
    } catch (error) {
      console.error('Failed to load production orders:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const stats = await productionOrderService.getStatistics()
      setStatistics(stats)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const handleDelete = async (order: ProductionOrder) => {
    if (!confirm(`Are you sure you want to delete production order ${order.order_number}?`)) return

    try {
      await productionOrderService.delete(order.id)
      loadOrders()
      loadStatistics()
    } catch (error) {
      console.error('Failed to delete production order:', error)
      alert('Failed to delete production order')
    }
  }

  const getStatusBadge = (status: ProductionOrderStatus) => {
    const badges = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock },
      in_progress: { bg: 'bg-blue-100', text: 'text-blue-800', icon: PlayCircle },
      paused: { bg: 'bg-orange-100', text: 'text-orange-800', icon: PauseCircle },
      completed: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
      cancelled: { bg: 'bg-red-100', text: 'text-red-800', icon: XCircle },
    }
    return badges[status] || badges.pending
  }

  const formatStatus = (status: string) => {
    return status.split('_').map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  }

  const getProgressPercentage = (produced: number, target: number) => {
    return target > 0 ? Math.min(Math.round((produced / target) * 100), 100) : 0
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Production Orders</h1>
            <p className="text-gray-600 mt-1">Manage and track production orders</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                loadOrders()
                loadStatistics()
              }}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={() => navigate('/production/orders/new')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              New Production Order
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Orders</p>
                  <p className="text-2xl font-bold text-gray-800">{statistics.total}</p>
                </div>
                <ClipboardList className="w-8 h-8 text-blue-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Pending</p>
                  <p className="text-2xl font-bold text-yellow-600">{statistics.pending}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold text-blue-600">{statistics.in_progress}</p>
                </div>
                <PlayCircle className="w-8 h-8 text-blue-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.completed}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>
            </div>
          </div>
        )}

        {/* Additional Statistics */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Paused</p>
                  <p className="text-2xl font-bold text-orange-600">{statistics.paused}</p>
                </div>
                <PauseCircle className="w-8 h-8 text-orange-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Produced</p>
                  <p className="text-2xl font-bold text-green-600">
                    {statistics.total_produced.toFixed(0)}
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Completion Rate</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {statistics.completion_rate.toFixed(1)}%
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-blue-500" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
                placeholder="Search by order number or product..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filters.status}
              onChange={(e) =>
                setFilters({ ...filters, status: e.target.value as ProductionOrderStatus | '', page: 1 })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="paused">Paused</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading production orders...</p>
          </div>
        ) : orders.length === 0 ? (
          <div className="p-8 text-center">
            <ClipboardList className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No production orders found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Order Number
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Product
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Progress
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Priority
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {orders.map((order) => {
                    const statusBadge = getStatusBadge(order.status)
                    const StatusIcon = statusBadge.icon
                    const progress = getProgressPercentage(order.produced_quantity, order.target_quantity)
                    return (
                      <tr key={order.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{order.order_number}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{order.product_name}</div>
                          {order.product_code && (
                            <div className="text-sm text-gray-500">{order.product_code}</div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${progress}%` }}
                              />
                            </div>
                            <span className="text-sm text-gray-600">{progress}%</span>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {order.produced_quantity}/{order.target_quantity} {order.unit}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-900">P{order.priority}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full ${statusBadge.bg} ${statusBadge.text} flex items-center gap-1 w-fit`}
                          >
                            <StatusIcon className="w-3 h-3" />
                            {formatStatus(order.status)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => navigate(`/production/orders/${order.id}`)}
                              className="text-blue-600 hover:text-blue-900"
                              title="View Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => navigate(`/production/orders/${order.id}/edit`)}
                              className="text-green-600 hover:text-green-900"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(order)}
                              className="text-red-600 hover:text-red-900"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Page {filters.page} of {totalPages}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                  disabled={filters.page === 1}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                  disabled={filters.page === totalPages}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default ProductionOrdersPage
