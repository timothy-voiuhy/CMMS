import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ClipboardList,
  Edit,
  Trash2,
  User,
  Wrench,
  Calendar,
  Clock,
  AlertCircle,
  CheckCircle,
} from 'lucide-react'
import { workOrderService, type WorkOrder, type WorkOrderStatus } from '../../services/workOrder.service'
import { craftsmanService } from '../../services/craftsman.service'

const WorkOrderDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [workOrder, setWorkOrder] = useState<WorkOrder | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false)
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [craftsmen, setCraftsmen] = useState<any[]>([])
  const [selectedCraftsmanId, setSelectedCraftsmanId] = useState<number | null>(null)

  useEffect(() => {
    if (id && id !== 'new') {
      loadWorkOrder()
    }
  }, [id])

  const loadWorkOrder = async () => {
    if (!id || id === 'new') return

    const woId = parseInt(id)
    if (isNaN(woId)) {
      navigate('/maintenance/work-orders')
      return
    }

    try {
      setIsLoading(true)
      const data = await workOrderService.getById(woId)
      setWorkOrder(data)
    } catch (error) {
      console.error('Failed to load work order:', error)
      alert('Failed to load work order details')
    } finally {
      setIsLoading(false)
    }
  }

  const loadCraftsmen = async () => {
    try {
      const response = await craftsmanService.getAll({ limit: 100 })
      setCraftsmen(response.data)
    } catch (error) {
      console.error('Failed to load craftsmen:', error)
    }
  }

  const handleDelete = async () => {
    if (!id || !workOrder) return

    if (!confirm(`Are you sure you want to delete work order ${workOrder.work_order_number}?`))
      return

    try {
      await workOrderService.delete(parseInt(id))
      navigate('/maintenance/work-orders')
    } catch (error: any) {
      console.error('Failed to delete work order:', error)
      const detail = error.response?.data?.detail
      alert(typeof detail === 'string' ? detail : 'Failed to delete work order')
    }
  }

  const handleStatusChange = async (newStatus: WorkOrderStatus) => {
    if (!id) return

    try {
      setIsUpdatingStatus(true)
      await workOrderService.updateStatus(parseInt(id), newStatus)
      loadWorkOrder()
    } catch (error) {
      console.error('Failed to update status:', error)
      alert('Failed to update work order status')
    } finally {
      setIsUpdatingStatus(false)
    }
  }

  const handleAssign = async () => {
    if (!id || !selectedCraftsmanId) return

    try {
      await workOrderService.assign(parseInt(id), selectedCraftsmanId)
      setShowAssignModal(false)
      setSelectedCraftsmanId(null)
      loadWorkOrder()
    } catch (error) {
      console.error('Failed to assign work order:', error)
      alert('Failed to assign work order')
    }
  }

  const getStatusBadge = (status: WorkOrderStatus) => {
    const badges = {
      pending: { bg: 'bg-gray-100 dark:bg-gray-700', text: 'text-gray-800 dark:text-gray-300', icon: Clock },
      assigned: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-800 dark:text-blue-400', icon: User },
      in_progress: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-800 dark:text-yellow-400', icon: Clock },
      on_hold: { bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-800 dark:text-orange-400', icon: AlertCircle },
      completed: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-800 dark:text-green-400', icon: CheckCircle },
      cancelled: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-400', icon: AlertCircle },
    }
    return badges[status] || badges.pending
  }

  const getPriorityBadge = (priority: string) => {
    const badges = {
      low: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300',
      medium: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400',
      high: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-400',
      urgent: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400',
    }
    return badges[priority as keyof typeof badges] || badges.medium
  }

  const formatStatus = (status: string) => {
    return status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

  if (!workOrder) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-gray-500 dark:text-gray-400">Work order not found</p>
          <button
            onClick={() => navigate('/maintenance/work-orders')}
            className="mt-4 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
          >
            Back to Work Orders
          </button>
        </div>
      </div>
    )
  }

  const statusBadge = getStatusBadge(workOrder.status)
  const StatusIcon = statusBadge.icon

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/maintenance/work-orders')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Work Orders
        </button>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="flex items-start gap-3 sm:gap-4">
              <div className="flex-shrink-0 h-16 w-16 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <ClipboardList className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{workOrder.title}</h1>
                <div className="flex flex-wrap items-center gap-2 sm:gap-4 mt-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">WO: {workOrder.work_order_number}</span>
                  <span
                    className={`px-3 py-1 text-sm font-medium rounded-full ${statusBadge.bg} ${statusBadge.text} flex items-center gap-1`}
                  >
                    <StatusIcon className="w-4 h-4" />
                    {formatStatus(workOrder.status)}
                  </span>
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${getPriorityBadge(workOrder.priority)}`}>
                    {workOrder.priority.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center">
              {workOrder.status !== 'completed' && workOrder.status !== 'cancelled' && (
                <div className="relative">
                  <select
                    value={workOrder.status}
                    onChange={(e) => handleStatusChange(e.target.value as WorkOrderStatus)}
                    disabled={isUpdatingStatus}
                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
                  >
                    <option value="pending">Pending</option>
                    <option value="assigned">Assigned</option>
                    <option value="in_progress">In Progress</option>
                    <option value="on_hold">On Hold</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
              )}
              {!workOrder.assigned_to && (
                <button
                  onClick={() => {
                    setShowAssignModal(true)
                    loadCraftsmen()
                  }}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 dark:bg-green-500 rounded-lg hover:bg-green-700 dark:hover:bg-green-600"
                >
                  <User className="w-4 h-4" />
                  Assign
                </button>
              )}
              <button
                onClick={() => navigate(`/maintenance/work-orders/${id}/edit`)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={handleDelete}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-white dark:bg-gray-700 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Left Column - Info Cards */}
        <div className="space-y-4 sm:space-y-6">
          {/* Basic Info */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Work Order Details</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <ClipboardList className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Type</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{formatStatus(workOrder.work_order_type)}</p>
                </div>
              </div>
              {workOrder.equipment_id && (
                <div className="flex items-start gap-3">
                  <Wrench className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Equipment</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Equipment #{workOrder.equipment_id}</p>
                  </div>
                </div>
              )}
              {workOrder.assigned_to && (
                <div className="flex items-start gap-3">
                  <User className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Assigned To</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Craftsman #{workOrder.assigned_to}</p>
                  </div>
                </div>
              )}
              {workOrder.estimated_hours && (
                <div className="flex items-start gap-3">
                  <Clock className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Estimated Hours</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{workOrder.estimated_hours}h</p>
                  </div>
                </div>
              )}
              {workOrder.actual_hours && (
                <div className="flex items-start gap-3">
                  <Clock className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Actual Hours</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{workOrder.actual_hours}h</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Dates */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Timeline</h2>
            <div className="space-y-4">
              {workOrder.scheduled_date && (
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Scheduled Date</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{formatDate(workOrder.scheduled_date)}</p>
                </div>
              )}
              {workOrder.due_date && (
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Due Date</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{formatDate(workOrder.due_date)}</p>
                </div>
              )}
              {workOrder.started_at && (
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Started At</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{formatDate(workOrder.started_at)}</p>
                </div>
              )}
              {workOrder.completed_at && (
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Completed At</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{formatDate(workOrder.completed_at)}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Created At</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{formatDate(workOrder.created_at)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Description & Notes */}
        <div className="lg:col-span-2 space-y-4 sm:space-y-6">
          {/* Description */}
          {workOrder.description && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Description</h2>
              <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{workOrder.description}</p>
            </div>
          )}

          {/* Notes */}
          {workOrder.notes && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Notes</h2>
              <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{workOrder.notes}</p>
            </div>
          )}

          {/* Completion Notes */}
          {workOrder.completion_notes && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Completion Notes</h2>
              <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{workOrder.completion_notes}</p>
            </div>
          )}
        </div>
      </div>

      {/* Assign Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">Assign Work Order</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select Craftsman <span className="text-red-500">*</span>
                </label>
                <select
                  value={selectedCraftsmanId || ''}
                  onChange={(e) => setSelectedCraftsmanId(parseInt(e.target.value))}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select craftsman...</option>
                  {craftsmen.map((craftsman) => (
                    <option key={craftsman.id} value={craftsman.id}>
                      {craftsman.full_name} ({craftsman.employee_id})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:flex sm:justify-end mt-6">
              <button
                onClick={() => {
                  setShowAssignModal(false)
                  setSelectedCraftsmanId(null)
                }}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleAssign}
                disabled={!selectedCraftsmanId}
                className="px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                Assign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WorkOrderDetailPage
