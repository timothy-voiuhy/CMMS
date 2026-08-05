import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Edit,
  Trash2,
  Clock,
  Package,
  TrendingUp,
  AlertCircle,
  Calendar,
  Factory,
  Loader,
} from 'lucide-react'
import {
  productionOrderService,
  productionLineService,
  type ProductionOrder,
  type ProductionLine,
} from '../../services/production.service'

const ProductionOrderDetailPage: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [order, setOrder] = useState<ProductionOrder | null>(null)
  const [line, setLine] = useState<ProductionLine | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    if (!id || id === 'new') return
    
    try {
      setIsLoading(true)
      const orderId = parseInt(id)
      const orderData = await productionOrderService.getById(orderId)
      setOrder(orderData)
      
      if (orderData.production_line_id) {
        const lineData = await productionLineService.getById(orderData.production_line_id)
        setLine(lineData)
      }
    } catch (error) {
      console.error('Failed to load data:', error)
      alert('Failed to load production order')
      navigate('/production/orders')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!order || !confirm(`Are you sure you want to delete ${order.order_number}?`)) return

    try {
      await productionOrderService.delete(order.id)
      navigate('/production/orders')
    } catch (error) {
      console.error('Failed to delete production order:', error)
      alert('Failed to delete production order')
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
      ? Math.min(Math.round((order.produced_quantity / order.target_quantity) * 100), 100)
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
          onClick={() => navigate('/production/orders')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Production Orders
        </button>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{order.product_name}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">{order.order_number}</p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center sm:gap-3">
            <button
              onClick={() => navigate(`/production/orders/${order.id}/edit`)}
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
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-4 sm:mb-6">
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
            <p className="text-sm text-gray-600 dark:text-gray-400">Produced</p>
            <Package className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          </div>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
            {order.produced_quantity.toFixed(0)}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">of {order.target_quantity.toFixed(0)} {order.unit}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">Priority</p>
            <AlertCircle className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">P{order.priority}</p>
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
                  <p className="text-sm text-gray-600 dark:text-gray-400">Produced Quantity</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                    {order.produced_quantity.toFixed(2)} {order.unit}
                  </p>
                </div>
              </div>
              {order.defect_quantity && order.defect_quantity > 0 && (
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Defect Quantity</p>
                  <p className="text-sm font-medium text-red-600 dark:text-red-400 mt-1">
                    {order.defect_quantity.toFixed(2)} {order.unit}
                  </p>
                </div>
              )}
              {order.notes && (
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Notes</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100 mt-1">{order.notes}</p>
                </div>
              )}
              {order.completion_notes && (
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Completion Notes</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100 mt-1">{order.completion_notes}</p>
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
          {/* Production Line */}
          {line && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                <Factory className="w-5 h-5" />
                Production Line
              </h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Line Name</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">{line.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Line Code</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">{line.line_code}</p>
                </div>
                {line.location && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Location</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">{line.location}</p>
                  </div>
                )}
                <button
                  onClick={() => navigate(`/production/lines/${line.id}`)}
                  className="w-full mt-4 px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50"
                >
                  View Line Details
                </button>
              </div>
            </div>
          )}

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

export default ProductionOrderDetailPage
