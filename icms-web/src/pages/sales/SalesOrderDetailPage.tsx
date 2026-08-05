import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Edit, PackageCheck, Send, ShoppingCart, XCircle } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import {
  salesService,
  type SalesOrder,
  type SalesOrderItem,
  type SalesOrderPriority,
  type SalesOrderStatus,
} from '../../services/sales.service'

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

const remainingQuantity = (line: SalesOrderItem) => Math.max(0, line.ordered_quantity - line.fulfilled_quantity)

const getErrorMessage = (error: unknown, fallback: string) => {
  const response = (error as { response?: { data?: { detail?: unknown } } }).response
  return typeof response?.data?.detail === 'string' ? response.data.detail : fallback
}

const SalesOrderDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { hasPermission } = useAuthStore()
  const [order, setOrder] = useState<SalesOrder | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [fulfillmentQuantities, setFulfillmentQuantities] = useState<Record<number, number>>({})
  const [fulfillmentNotes, setFulfillmentNotes] = useState('')

  const canEdit = hasPermission('sales.orders.edit')
  const canConfirm = hasPermission('sales.orders.confirm')
  const canFulfill = hasPermission('sales.orders.fulfill') || hasPermission('inventory.transaction')
  const canCancel = hasPermission('sales.orders.cancel')

  const loadOrder = useCallback(async () => {
    if (!id) return
    try {
      setIsLoading(true)
      const data = await salesService.getOrderById(parseInt(id))
      setOrder(data)
      const nextFulfillment: Record<number, number> = {}
      for (const line of data.items || []) {
        nextFulfillment[line.id] = Math.min(remainingQuantity(line), line.item?.quantity ?? remainingQuantity(line))
      }
      setFulfillmentQuantities(nextFulfillment)
    } catch (error) {
      console.error('Failed to load sales order:', error)
      alert('Failed to load sales order')
      navigate('/sales/orders')
    } finally {
      setIsLoading(false)
    }
  }, [id, navigate])

  useEffect(() => {
    void Promise.resolve().then(loadOrder)
  }, [loadOrder])

  const totals = useMemo(() => {
    const lines = order?.items || []
    return {
      ordered: lines.reduce((sum, line) => sum + line.ordered_quantity, 0),
      fulfilled: lines.reduce((sum, line) => sum + line.fulfilled_quantity, 0),
      remaining: lines.reduce((sum, line) => sum + remainingQuantity(line), 0),
    }
  }, [order])

  const runAction = async (action: () => Promise<SalesOrder>) => {
    try {
      setIsSaving(true)
      const updated = await action()
      setOrder(updated)
      await loadOrder()
    } catch (error: unknown) {
      console.error('Sales order action failed:', error)
      alert(getErrorMessage(error, 'Sales order action failed'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleConfirm = () => {
    if (!order) return
    runAction(() => salesService.confirmOrder(order.id))
  }

  const handleFulfill = () => {
    if (!order) return
    const lines = (order.items || [])
      .map((line) => ({
        line_id: line.id,
        quantity: Number(fulfillmentQuantities[line.id] || 0),
      }))
      .filter((line) => line.quantity > 0)

    if (lines.length === 0) {
      alert('Enter at least one fulfillment quantity')
      return
    }

    runAction(() => salesService.fulfillOrder(order.id, {
      items: lines,
      notes: fulfillmentNotes || undefined,
    }))
  }

  const handleCancel = () => {
    if (!order) return
    const reason = prompt(`Reason for cancelling ${order.order_number}`)
    if (!reason?.trim()) return
    runAction(() => salesService.cancelOrder(order.id, { reason }))
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen text-gray-600 dark:text-gray-400">Loading sales order...</div>
  }

  if (!order) {
    return <div className="flex items-center justify-center h-screen text-gray-600 dark:text-gray-400">Sales order not found</div>
  }

  const lines = order.items || []
  const canShowFulfillment = ['confirmed', 'partially_fulfilled'].includes(order.status) && canFulfill

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <button onClick={() => navigate('/sales/orders')} className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Sales Orders
        </button>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 h-14 w-14 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <ShoppingCart className="w-7 h-7 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{order.order_number}</h1>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusClass(order.status)}`}>{formatLabel(order.status)}</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityClass(order.priority)}`}>{formatLabel(order.priority)}</span>
                </div>
                <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-600 dark:text-gray-400">
                  <span>{order.customer?.name || `Customer #${order.customer_id}`}</span>
                  {order.order_date && <span>Ordered {new Date(order.order_date).toLocaleDateString()}</span>}
                  {order.requested_delivery_date && <span>Delivery {new Date(order.requested_delivery_date).toLocaleDateString()}</span>}
                  <span>{formatMoney(order.total_amount, order.currency)}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:justify-end">
              {order.status === 'draft' && canEdit && (
                <button onClick={() => navigate(`/sales/orders/${order.id}/edit`)} className="flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600">
                  <Edit className="w-4 h-4" />
                  Edit
                </button>
              )}
              {order.status === 'draft' && canConfirm && (
                <button onClick={handleConfirm} disabled={isSaving} className="flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50">
                  <Send className="w-4 h-4" />
                  Confirm
                </button>
              )}
              {['draft', 'confirmed'].includes(order.status) && canCancel && (
                <button onClick={handleCancel} disabled={isSaving} className="flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-white dark:bg-gray-700 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 disabled:opacity-50">
                  <XCircle className="w-4 h-4" />
                  Cancel
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">Ordered Quantity</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{totals.ordered}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">Fulfilled Quantity</p>
          <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{totals.fulfilled}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">Remaining Quantity</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{totals.remaining}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">Order Total</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{formatMoney(order.total_amount, order.currency)}</p>
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
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Ordered</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Fulfilled</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Remaining</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Line Total</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {lines.map((line) => {
                const insufficient = canShowFulfillment && (line.item?.quantity || 0) < remainingQuantity(line)
                return (
                  <tr key={line.id} className={insufficient ? 'bg-red-50 dark:bg-red-900/10' : undefined}>
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{line.item_name}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{line.item_code}</div>
                      {line.notes && <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{line.notes}</div>}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{line.item ? `${line.item.quantity} ${line.unit_of_measure}` : '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{line.ordered_quantity} {line.unit_of_measure}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{line.fulfilled_quantity} {line.unit_of_measure}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{remainingQuantity(line)} {line.unit_of_measure}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium text-gray-900 dark:text-gray-100">{formatMoney(line.line_total, order.currency)}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">{formatLabel(line.status)}</span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {canShowFulfillment && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Fulfillment</h2>
          <div className="space-y-3">
            {lines.map((line) => (
              <div key={line.id} className="grid grid-cols-1 sm:grid-cols-[1fr_180px] gap-3 items-center">
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{line.item_name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Remaining {remainingQuantity(line)} {line.unit_of_measure}; available {line.item?.quantity ?? 0}</p>
                </div>
                <input type="number" step="0.01" min="0" max={remainingQuantity(line)} value={fulfillmentQuantities[line.id] || 0} onChange={(event) => setFulfillmentQuantities({ ...fulfillmentQuantities, [line.id]: Number(event.target.value) })} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            ))}
          </div>
          <textarea value={fulfillmentNotes} onChange={(event) => setFulfillmentNotes(event.target.value)} rows={3} placeholder="Fulfillment notes" className="mt-4 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <div className="mt-4 flex justify-end">
            <button onClick={handleFulfill} disabled={isSaving} className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-emerald-600 dark:bg-emerald-500 rounded-lg hover:bg-emerald-700 dark:hover:bg-emerald-600 disabled:opacity-50">
              <PackageCheck className="w-4 h-4" />
              Fulfill Selected
            </button>
          </div>
        </div>
      )}

      {order.status === 'fulfilled' && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-center gap-2 text-green-800 dark:text-green-300">
          <CheckCircle2 className="w-5 h-5" />
          This sales order has been fulfilled.
        </div>
      )}
    </div>
  )
}

export default SalesOrderDetailPage
