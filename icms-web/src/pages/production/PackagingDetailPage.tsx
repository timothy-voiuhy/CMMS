import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Edit,
  Trash2,
  Clock,
  Package,
  TrendingUp,
  PackageCheck,
  Calendar,
  Loader,
} from 'lucide-react'
import {
  packagingOrderService,
  type PackagingOrder,
} from '../../services/production.service'

const PackagingDetailPage: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [order, setOrder] = useState<PackagingOrder | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    if (!id || id === 'new') return
    
    try {
      setIsLoading(true)
      const orderId = parseInt(id)
      const orderData = await packagingOrderService.getById(orderId)
      setOrder(orderData)
    } catch (error) {
      console.error('Failed to load data:', error)
      alert('Failed to load packaging order')
      navigate('/production/packaging')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!order || !confirm(`Are you sure you want to delete ${order.order_number}?`)) return

    try {
      await packagingOrderService.delete(order.id)
      navigate('/production/packaging')
    } catch (error) {
      console.error('Failed to delete packaging order:', error)
      alert('Failed to delete packaging order')
    }
  }

  const getStatusColor = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800',
      paused: 'bg-orange-100 text-orange-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    }
    return colors[status as keyof typeof colors] || colors.pending
  }

  const formatStatus = (status: string) => {
    return status.split('_').map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  }

  const getProgressPercentage = () => {
    if (!order) return 0
    return order.target_quantity > 0
      ? Math.min(Math.round((order.packaged_quantity / order.target_quantity) * 100), 100)
      : 0
  }

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'Not set'
    return new Date(dateString).toLocaleString()
  }

  if (isLoading || !order) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-400" />
      </div>
    )
  }

  const progress = getProgressPercentage()

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/production/packaging')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Packaging Orders
        </button>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{order.product_name}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">{order.order_number}</p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center sm:gap-3">
            <button
              onClick={() => navigate(`/production/packaging/${order.id}/edit`)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              <Edit className="w-4 h-4" />
              Edit
            </button>
            <button
              onClick={handleDelete}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-red-600 dark:bg-red-500 rounded-lg hover:bg-red-700 dark:hover:bg-red-600"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Status and Progress Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
            <Clock className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          </div>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
            {formatStatus(order.status)}
          </span>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">Progress</p>
            <TrendingUp className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{progress}%</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">Packaged</p>
            <Package className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          </div>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
            {order.packaged_quantity.toFixed(0)}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">of {order.target_quantity.toFixed(0)} {order.unit}</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Order Details */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Order Details</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Product Name</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">{order.product_name}</p>
                </div>
                {order.product_code && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Product Code</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">{order.product_code}</p>
                  </div>
                )}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Target Quantity</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {order.target_quantity.toFixed(2)} {order.unit}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Packaged Quantity</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {order.packaged_quantity.toFixed(2)} {order.unit}
                  </p>
                </div>
              </div>
              {order.notes && (
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Notes</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100 mt-1">{order.notes}</p>
                </div>
              )}
            </div>
          </div>

          {/* Packaging Details */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
              <PackageCheck className="w-5 h-5" />
              Packaging Details
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Packaging Type</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {order.packaging_type || 'Not specified'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Packaging Material</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {order.packaging_material || 'Not specified'}
                  </p>
                </div>
              </div>
              {order.units_per_package && (
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Units per Package</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {order.units_per_package}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Schedule */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Schedule
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Scheduled Start</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {formatDate(order.scheduled_start)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Scheduled End</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {formatDate(order.scheduled_end)}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Actual Start</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {formatDate(order.actual_start)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Actual End</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {formatDate(order.actual_end)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4 sm:space-y-6">
          {/* Metadata */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Metadata</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Created</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                  {new Date(order.created_at).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Last Updated</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                  {new Date(order.updated_at).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PackagingDetailPage
