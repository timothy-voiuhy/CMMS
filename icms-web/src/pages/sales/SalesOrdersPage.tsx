import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, Clock, Eye, FilePlus2, PackageCheck, RefreshCw, Search, ShoppingCart } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import {
  salesService,
  type SalesOrder,
  type SalesOrderPriority,
  type SalesOrderStatus,
  type SalesStatistics,
} from '../../services/sales.service'

const STATUS_OPTIONS: { value: SalesOrderStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'partially_fulfilled', label: 'Partially Fulfilled' },
  { value: 'fulfilled', label: 'Fulfilled' },
  { value: 'cancelled', label: 'Cancelled' },
]

const PRIORITY_OPTIONS: { value: SalesOrderPriority | ''; label: string }[] = [
  { value: '', label: 'All Priorities' },
  { value: 'urgent', label: 'Urgent' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
]

const formatLabel = (value: string) => value.split('_').map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(' ')

const formatMoney = (value: number, currency = 'USD') => {
  return new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(value || 0)
}

const statusClass = (status: SalesOrderStatus) => {
  switch (status) {
    case 'draft':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
    case 'confirmed':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
    case 'partially_fulfilled':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
    case 'fulfilled':
      return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
    case 'cancelled':
      return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }
}

const priorityClass = (priority: SalesOrderPriority) => {
  switch (priority) {
    case 'urgent':
      return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
    case 'high':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
    case 'medium':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
    case 'low':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }
}

const SalesOrdersPage: React.FC = () => {
  const navigate = useNavigate()
  const { hasPermission } = useAuthStore()
  const [orders, setOrders] = useState<SalesOrder[]>([])
  const [statistics, setStatistics] = useState<SalesStatistics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    search: '',
    status: '' as SalesOrderStatus | '',
    priority: '' as SalesOrderPriority | '',
  })

  const canCreate = hasPermission('sales.orders.create')

  const loadOrders = useCallback(async () => {
    try {
      setIsLoading(true)
      const [ordersResponse, statsResponse] = await Promise.all([
        salesService.getOrders({
          page: filters.page,
          limit: filters.limit,
          search: filters.search || undefined,
          status: filters.status || undefined,
          priority: filters.priority || undefined,
        }),
        salesService.getStatistics(),
      ])
      setOrders(ordersResponse.data)
      setTotalPages(ordersResponse.totalPages)
      setStatistics(statsResponse)
    } catch (error) {
      console.error('Failed to load sales orders:', error)
    } finally {
      setIsLoading(false)
    }
  }, [filters])

  useEffect(() => {
    void Promise.resolve().then(loadOrders)
  }, [loadOrders])

  const localStats = useMemo(() => ({
    confirmed: statistics?.confirmed ?? orders.filter((order) => order.status === 'confirmed').length,
    partial: statistics?.partially_fulfilled ?? orders.filter((order) => order.status === 'partially_fulfilled').length,
    fulfilled: statistics?.fulfilled ?? orders.filter((order) => order.status === 'fulfilled').length,
    openValue: statistics?.open_value ?? orders.filter((order) => ['confirmed', 'partially_fulfilled'].includes(order.status)).reduce((sum, order) => sum + order.total_amount, 0),
  }), [orders, statistics])

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Sales Orders</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Create, confirm, and dispatch customer orders</p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center sm:gap-3">
            <button
              onClick={loadOrders}
              className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            {canCreate && (
              <button
                onClick={() => navigate('/sales/orders/new')}
                className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
              >
                <FilePlus2 className="w-4 h-4" />
                New Order
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Confirmed</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{localStats.confirmed}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-500 dark:text-blue-400" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Partial</p>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{localStats.partial}</p>
              </div>
              <PackageCheck className="w-8 h-8 text-yellow-500 dark:text-yellow-400" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Fulfilled</p>
                <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{localStats.fulfilled}</p>
              </div>
              <CheckCircle2 className="w-8 h-8 text-emerald-500 dark:text-emerald-400" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Open Value</p>
                <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{formatMoney(localStats.openValue)}</p>
              </div>
              <ShoppingCart className="w-8 h-8 text-gray-500 dark:text-gray-400" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                value={filters.search}
                onChange={(event) => setFilters({ ...filters, search: event.target.value, page: 1 })}
                placeholder="Search order number, customer, or notes..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
            <select value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value as SalesOrderStatus | '', page: 1 })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
              {STATUS_OPTIONS.map((option) => <option key={option.value || 'all'} value={option.value}>{option.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Priority</label>
            <select value={filters.priority} onChange={(event) => setFilters({ ...filters, priority: event.target.value as SalesOrderPriority | '', page: 1 })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
              {PRIORITY_OPTIONS.map((option) => <option key={option.value || 'all'} value={option.value}>{option.label}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-600 dark:text-gray-400">Loading sales orders...</div>
        ) : orders.length === 0 ? (
          <div className="p-8 text-center text-gray-600 dark:text-gray-400">No sales orders found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Order</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Customer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Priority</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Delivery</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {orders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{order.order_number}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{order.line_count} line{order.line_count === 1 ? '' : 's'}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">{order.customer?.name || `Customer #${order.customer_id}`}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusClass(order.status)}`}>{formatLabel(order.status)}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityClass(order.priority)}`}>{formatLabel(order.priority)}</span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">{order.requested_delivery_date ? new Date(order.requested_delivery_date).toLocaleDateString() : '-'}</td>
                    <td className="px-6 py-4 text-right text-sm font-medium text-gray-900 dark:text-gray-100">{formatMoney(order.total_amount, order.currency)}</td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => navigate(`/sales/orders/${order.id}`)} className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300" title="View Details">
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <button onClick={() => setFilters({ ...filters, page: Math.max(1, filters.page - 1) })} disabled={filters.page === 1} className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 text-gray-700 dark:text-gray-200">Previous</button>
            <span className="text-sm text-gray-600 dark:text-gray-400">Page {filters.page} of {totalPages}</span>
            <button onClick={() => setFilters({ ...filters, page: Math.min(totalPages, filters.page + 1) })} disabled={filters.page === totalPages} className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 text-gray-700 dark:text-gray-200">Next</button>
          </div>
        )}
      </div>
    </div>
  )
}

export default SalesOrdersPage
