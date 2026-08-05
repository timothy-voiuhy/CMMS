import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  CheckCircle2,
  ClipboardList,
  Edit,
  PackageCheck,
  Send,
  XCircle,
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import {
  inventoryService,
  type InventoryRequisition,
  type InventoryRequisitionItem,
  type RequisitionPriority,
  type RequisitionStatus,
} from '../../services/inventory.service'

const formatLabel = (value: string) => value.split('_').map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(' ')

const statusClass = (status: RequisitionStatus) => {
  switch (status) {
    case 'draft':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
    case 'submitted':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
    case 'approved':
      return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300'
    case 'partially_fulfilled':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
    case 'fulfilled':
      return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
    case 'rejected':
      return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
    case 'cancelled':
      return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-200'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }
}

const priorityClass = (priority: RequisitionPriority) => {
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

const remainingApproved = (line: InventoryRequisitionItem) => {
  const approved = line.approved_quantity ?? line.requested_quantity
  return Math.max(0, approved - line.fulfilled_quantity)
}

const InventoryRequisitionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { hasPermission } = useAuthStore()
  const [requisition, setRequisition] = useState<InventoryRequisition | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [approvalQuantities, setApprovalQuantities] = useState<Record<number, number>>({})
  const [fulfillmentQuantities, setFulfillmentQuantities] = useState<Record<number, number>>({})
  const [approvalNotes, setApprovalNotes] = useState('')
  const [fulfillmentNotes, setFulfillmentNotes] = useState('')
  const [rejectReason, setRejectReason] = useState('')

  const canEdit = hasPermission('inventory.requisitions.edit') || hasPermission('inventory.edit')
  const canSubmit = hasPermission('inventory.requisitions.submit') || hasPermission('inventory.create')
  const canApprove = hasPermission('inventory.requisitions.approve') || hasPermission('inventory.edit')
  const canFulfill = hasPermission('inventory.requisitions.fulfill') || hasPermission('inventory.transaction') || hasPermission('inventory.adjust')
  const canCancel = hasPermission('inventory.requisitions.cancel') || hasPermission('inventory.edit')

  useEffect(() => {
    loadRequisition()
  }, [id])

  const loadRequisition = async () => {
    if (!id) return

    try {
      setIsLoading(true)
      const data = await inventoryService.getRequisitionById(parseInt(id))
      setRequisition(data)
      const nextApproval: Record<number, number> = {}
      const nextFulfillment: Record<number, number> = {}
      for (const line of data.items || []) {
        nextApproval[line.id] = line.approved_quantity ?? line.requested_quantity
        nextFulfillment[line.id] = Math.min(remainingApproved(line), line.item?.quantity ?? remainingApproved(line))
      }
      setApprovalQuantities(nextApproval)
      setFulfillmentQuantities(nextFulfillment)
    } catch (error) {
      console.error('Failed to load requisition:', error)
      alert('Failed to load requisition')
      navigate('/inventory/requisitions')
    } finally {
      setIsLoading(false)
    }
  }

  const totals = useMemo(() => {
    const lines = requisition?.items || []
    return {
      requested: lines.reduce((sum, line) => sum + line.requested_quantity, 0),
      approved: lines.reduce((sum, line) => sum + (line.approved_quantity ?? 0), 0),
      fulfilled: lines.reduce((sum, line) => sum + line.fulfilled_quantity, 0),
    }
  }, [requisition])

  const runAction = async (action: () => Promise<InventoryRequisition>) => {
    try {
      setIsSaving(true)
      const updated = await action()
      setRequisition(updated)
      await loadRequisition()
    } catch (error: any) {
      console.error('Requisition action failed:', error)
      const detail = error.response?.data?.detail
      alert(typeof detail === 'string' ? detail : 'Requisition action failed')
    } finally {
      setIsSaving(false)
    }
  }

  const handleSubmit = () => {
    if (!requisition) return
    runAction(() => inventoryService.submitRequisition(requisition.id))
  }

  const handleApprove = () => {
    if (!requisition) return
    runAction(() => inventoryService.approveRequisition(requisition.id, {
      items: (requisition.items || []).map((line) => ({
        line_id: line.id,
        approved_quantity: Number(approvalQuantities[line.id] || 0),
      })),
      notes: approvalNotes || undefined,
    }))
  }

  const handleReject = () => {
    if (!requisition) return
    if (!rejectReason.trim()) {
      alert('Rejection reason is required')
      return
    }
    runAction(() => inventoryService.rejectRequisition(requisition.id, { reason: rejectReason }))
  }

  const handleFulfill = () => {
    if (!requisition) return
    const lines = (requisition.items || [])
      .map((line) => ({
        line_id: line.id,
        quantity: Number(fulfillmentQuantities[line.id] || 0),
      }))
      .filter((line) => line.quantity > 0)

    if (lines.length === 0) {
      alert('Enter at least one fulfillment quantity')
      return
    }

    runAction(() => inventoryService.fulfillRequisition(requisition.id, {
      items: lines,
      notes: fulfillmentNotes || undefined,
    }))
  }

  const handleCancel = () => {
    if (!requisition) return
    if (!confirm(`Cancel ${requisition.requisition_number}?`)) return
    runAction(() => inventoryService.cancelRequisition(requisition.id))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

  if (!requisition) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-gray-500 dark:text-gray-400">Requisition not found</p>
          <button
            onClick={() => navigate('/inventory/requisitions')}
            className="mt-4 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-500"
          >
            Back to Requisitions
          </button>
        </div>
      </div>
    )
  }

  const lines = requisition.items || []
  const canShowApproval = requisition.status === 'submitted' && canApprove
  const canShowFulfillment = ['approved', 'partially_fulfilled'].includes(requisition.status) && canFulfill

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <button
          onClick={() => navigate('/inventory/requisitions')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Requisitions
        </button>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 h-14 w-14 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <ClipboardList className="w-7 h-7 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{requisition.title}</h1>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusClass(requisition.status)}`}>
                    {formatLabel(requisition.status)}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityClass(requisition.priority)}`}>
                    {formatLabel(requisition.priority)}
                  </span>
                </div>
                <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-600 dark:text-gray-400">
                  <span>{requisition.requisition_number}</span>
                  {requisition.department && <span>{requisition.department}</span>}
                  {requisition.needed_by && <span>Needed {new Date(requisition.needed_by).toLocaleDateString()}</span>}
                  {requisition.work_order_id && <span>WO #{requisition.work_order_id}</span>}
                  {requisition.production_order_id && <span>Production #{requisition.production_order_id}</span>}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:justify-end">
              {requisition.status === 'draft' && canEdit && (
                <button
                  onClick={() => navigate(`/inventory/requisitions/${requisition.id}/edit`)}
                  className="flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  <Edit className="w-4 h-4" />
                  Edit
                </button>
              )}
              {requisition.status === 'draft' && canSubmit && (
                <button
                  onClick={handleSubmit}
                  disabled={isSaving}
                  className="flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                  Submit
                </button>
              )}
              {['draft', 'submitted', 'approved'].includes(requisition.status) && canCancel && (
                <button
                  onClick={handleCancel}
                  disabled={isSaving}
                  className="flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-white dark:bg-gray-700 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  Cancel
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">Requested Quantity</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{totals.requested}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">Approved Quantity</p>
          <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{totals.approved}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">Fulfilled Quantity</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{totals.fulfilled}</p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div className="px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Line Items</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Item</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Available</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Requested</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Approved</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Fulfilled</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Remaining</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {lines.map((line) => {
                const insufficient = canShowFulfillment && (line.item?.quantity || 0) < remainingApproved(line)
                return (
                  <tr key={line.id} className={insufficient ? 'bg-red-50 dark:bg-red-900/10' : undefined}>
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{line.item?.name || `Item #${line.item_id}`}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{line.item?.item_code}</div>
                      {line.notes && <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{line.notes}</div>}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                      {line.item ? `${line.item.quantity} ${line.unit_of_measure}` : '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{line.requested_quantity} {line.unit_of_measure}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{line.approved_quantity ?? '-'} {line.approved_quantity != null ? line.unit_of_measure : ''}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{line.fulfilled_quantity} {line.unit_of_measure}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{remainingApproved(line)} {line.unit_of_measure}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                        {formatLabel(line.status)}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {canShowApproval && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Approval</h2>
          <div className="space-y-3">
            {lines.map((line) => (
              <div key={line.id} className="grid grid-cols-1 sm:grid-cols-[1fr_180px] gap-3 items-center">
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{line.item?.name || `Item #${line.item_id}`}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Requested {line.requested_quantity} {line.unit_of_measure}</p>
                </div>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max={line.requested_quantity}
                  value={approvalQuantities[line.id] ?? line.requested_quantity}
                  onChange={(event) => setApprovalQuantities({ ...approvalQuantities, [line.id]: parseFloat(event.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
            <textarea
              value={approvalNotes}
              onChange={(event) => setApprovalNotes(event.target.value)}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Approval notes"
            />
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_auto_auto]">
              <input
                type="text"
                value={rejectReason}
                onChange={(event) => setRejectReason(event.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Rejection reason"
              />
              <button
                onClick={handleReject}
                disabled={isSaving}
                className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-white dark:bg-gray-700 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 disabled:opacity-50"
              >
                <XCircle className="w-4 h-4" />
                Reject
              </button>
              <button
                onClick={handleApprove}
                disabled={isSaving}
                className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-emerald-600 dark:bg-emerald-500 rounded-lg hover:bg-emerald-700 dark:hover:bg-emerald-600 disabled:opacity-50"
              >
                <CheckCircle2 className="w-4 h-4" />
                Approve
              </button>
            </div>
          </div>
        </div>
      )}

      {canShowFulfillment && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Fulfillment</h2>
          <div className="space-y-3">
            {lines.filter((line) => remainingApproved(line) > 0).map((line) => (
              <div key={line.id} className="grid grid-cols-1 sm:grid-cols-[1fr_180px] gap-3 items-center">
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{line.item?.name || `Item #${line.item_id}`}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Remaining {remainingApproved(line)} {line.unit_of_measure}, available {line.item?.quantity ?? 0}
                  </p>
                </div>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max={remainingApproved(line)}
                  value={fulfillmentQuantities[line.id] ?? 0}
                  onChange={(event) => setFulfillmentQuantities({ ...fulfillmentQuantities, [line.id]: parseFloat(event.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}
            <textarea
              value={fulfillmentNotes}
              onChange={(event) => setFulfillmentNotes(event.target.value)}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Fulfillment notes"
            />
            <div className="flex justify-end">
              <button
                onClick={handleFulfill}
                disabled={isSaving}
                className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                <PackageCheck className="w-4 h-4" />
                Fulfill
              </button>
            </div>
          </div>
        </div>
      )}

      {(requisition.description || requisition.notes || requisition.rejection_reason) && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mt-6">
          {requisition.description && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase mb-2">Description</h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">{requisition.description}</p>
            </div>
          )}
          {requisition.notes && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase mb-2">Notes</h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">{requisition.notes}</p>
            </div>
          )}
          {requisition.rejection_reason && (
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase mb-2">Rejection Reason</h3>
              <p className="text-sm text-red-700 dark:text-red-300">{requisition.rejection_reason}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default InventoryRequisitionDetailPage
