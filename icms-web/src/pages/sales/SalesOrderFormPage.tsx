import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Plus, Save, Send, Trash2 } from 'lucide-react'
import { inventoryService, type InventoryItem } from '../../services/inventory.service'
import {
  salesService,
  type CreateSalesOrderLine,
  type CreateSalesOrderRequest,
  type Customer,
  type SalesOrderPriority,
} from '../../services/sales.service'

const emptyLine = (): CreateSalesOrderLine => ({
  item_id: 0,
  ordered_quantity: 1,
  unit_price: 0,
  tax_rate: 0,
  discount_amount: 0,
  notes: '',
})

const lineTotal = (line: CreateSalesOrderLine) => {
  const subtotal = Number(line.ordered_quantity || 0) * Number(line.unit_price || 0)
  const tax = subtotal * (Number(line.tax_rate || 0) / 100)
  return Math.max(0, subtotal + tax - Number(line.discount_amount || 0))
}

const getErrorMessage = (error: unknown, fallback: string) => {
  const response = (error as { response?: { data?: { detail?: unknown } } }).response
  return typeof response?.data?.detail === 'string' ? response.data.detail : fallback
}

const SalesOrderFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditMode = Boolean(id)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [customers, setCustomers] = useState<Customer[]>([])
  const [items, setItems] = useState<InventoryItem[]>([])
  const [formData, setFormData] = useState<CreateSalesOrderRequest>({
    customer_id: 0,
    priority: 'medium',
    order_date: new Date().toISOString().split('T')[0],
    requested_delivery_date: '',
    currency: 'USD',
    notes: '',
    items: [emptyLine()],
  })

  const itemsById = useMemo(() => new Map(items.map((item) => [item.id, item])), [items])
  const totals = useMemo(() => {
    const subtotal = formData.items.reduce((sum, line) => sum + Number(line.ordered_quantity || 0) * Number(line.unit_price || 0), 0)
    const tax = formData.items.reduce((sum, line) => sum + Number(line.ordered_quantity || 0) * Number(line.unit_price || 0) * (Number(line.tax_rate || 0) / 100), 0)
    const discount = formData.items.reduce((sum, line) => sum + Number(line.discount_amount || 0), 0)
    return {
      subtotal,
      tax,
      discount,
      total: Math.max(0, subtotal + tax - discount),
    }
  }, [formData.items])

  const loadLookups = useCallback(async () => {
    try {
      const [customerResponse, inventoryResponse] = await Promise.all([
        salesService.getCustomers({ limit: 100 }),
        inventoryService.getAll({ limit: 100 }),
      ])
      setCustomers(customerResponse.data)
      setItems(inventoryResponse.data)
    } catch (error) {
      console.error('Failed to load sales lookups:', error)
    }
  }, [])

  const loadOrder = useCallback(async () => {
    if (!id) return
    try {
      setIsLoading(true)
      const order = await salesService.getOrderById(parseInt(id))
      if (order.status !== 'draft') {
        alert('Only draft sales orders can be edited')
        navigate(`/sales/orders/${id}`)
        return
      }
      setFormData({
        customer_id: order.customer_id,
        priority: order.priority,
        order_date: order.order_date || '',
        requested_delivery_date: order.requested_delivery_date || '',
        currency: order.currency || 'USD',
        notes: order.notes || '',
        items: (order.items || []).map((line) => ({
          item_id: line.item_id,
          ordered_quantity: line.ordered_quantity,
          unit_price: line.unit_price,
          tax_rate: line.tax_rate,
          discount_amount: line.discount_amount,
          notes: line.notes || '',
        })),
      })
    } catch (error) {
      console.error('Failed to load sales order:', error)
      alert('Failed to load sales order')
      navigate('/sales/orders')
    } finally {
      setIsLoading(false)
    }
  }, [id, navigate])

  useEffect(() => {
    void Promise.resolve().then(loadLookups)
  }, [loadLookups])

  useEffect(() => {
    if (isEditMode) {
      void Promise.resolve().then(loadOrder)
    }
  }, [isEditMode, loadOrder])

  const updateLine = (index: number, patch: Partial<CreateSalesOrderLine>) => {
    const nextLines = [...formData.items]
    nextLines[index] = { ...nextLines[index], ...patch }
    setFormData({ ...formData, items: nextLines })
  }

  const handleItemChange = (index: number, itemId: number) => {
    const selectedItem = itemsById.get(itemId)
    updateLine(index, {
      item_id: itemId,
      unit_price: selectedItem?.unit_cost || 0,
    })
  }

  const addLine = () => setFormData({ ...formData, items: [...formData.items, emptyLine()] })

  const removeLine = (index: number) => {
    if (formData.items.length === 1) return
    setFormData({ ...formData, items: formData.items.filter((_, lineIndex) => lineIndex !== index) })
  }

  const buildPayload = (): CreateSalesOrderRequest => ({
    ...formData,
    order_date: formData.order_date || undefined,
    requested_delivery_date: formData.requested_delivery_date || undefined,
    notes: formData.notes || undefined,
    items: formData.items.map((line) => ({
      item_id: Number(line.item_id),
      ordered_quantity: Number(line.ordered_quantity),
      unit_price: Number(line.unit_price),
      tax_rate: Number(line.tax_rate || 0),
      discount_amount: Number(line.discount_amount || 0),
      notes: line.notes || undefined,
    })),
  })

  const validate = () => {
    if (!formData.customer_id) {
      alert('Customer is required')
      return false
    }
    const itemIds = new Set<number>()
    for (const line of formData.items) {
      if (!line.item_id) {
        alert('Every line must select an item')
        return false
      }
      if (itemIds.has(line.item_id)) {
        alert('Duplicate items are not allowed')
        return false
      }
      itemIds.add(line.item_id)
      if (!line.ordered_quantity || line.ordered_quantity <= 0) {
        alert('Every line quantity must be greater than zero')
        return false
      }
      if (line.unit_price == null || line.unit_price < 0) {
        alert('Every line unit price must be zero or greater')
        return false
      }
    }
    return true
  }

  const saveDraft = async () => {
    if (!validate()) return null
    try {
      setIsSaving(true)
      if (isEditMode && id) {
        return await salesService.updateOrder(parseInt(id), buildPayload())
      }
      return await salesService.createOrder(buildPayload())
    } catch (error: unknown) {
      console.error('Failed to save sales order:', error)
      alert(getErrorMessage(error, 'Failed to save sales order'))
      return null
    } finally {
      setIsSaving(false)
    }
  }

  const handleSave = async () => {
    const order = await saveDraft()
    if (order) navigate(`/sales/orders/${order.id}`)
  }

  const handleConfirm = async () => {
    const order = await saveDraft()
    if (!order) return
    try {
      setIsSaving(true)
      const confirmed = await salesService.confirmOrder(order.id)
      navigate(`/sales/orders/${confirmed.id}`)
    } catch (error: unknown) {
      console.error('Failed to confirm sales order:', error)
      alert(getErrorMessage(error, 'Failed to confirm sales order'))
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen text-gray-600 dark:text-gray-400">Loading sales order...</div>
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <button onClick={() => navigate('/sales/orders')} className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Sales Orders
        </button>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{isEditMode ? 'Edit Sales Order' : 'New Sales Order'}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Prepare customer order lines before confirmation and dispatch</p>
          </div>
          <div className="grid grid-cols-1 gap-2 sm:flex sm:items-center sm:gap-3">
            <button onClick={handleSave} disabled={isSaving} className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50">
              <Save className="w-4 h-4" />
              Save Draft
            </button>
            <button onClick={handleConfirm} disabled={isSaving} className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50">
              <Send className="w-4 h-4" />
              Confirm
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Customer</label>
              <select value={formData.customer_id || ''} onChange={(event) => setFormData({ ...formData, customer_id: Number(event.target.value) })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">Select customer</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>{customer.customer_code} - {customer.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Priority</label>
              <select value={formData.priority} onChange={(event) => setFormData({ ...formData, priority: event.target.value as SalesOrderPriority })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Order Date</label>
              <input type="date" value={formData.order_date || ''} onChange={(event) => setFormData({ ...formData, order_date: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Requested Delivery</label>
              <input type="date" value={formData.requested_delivery_date || ''} onChange={(event) => setFormData({ ...formData, requested_delivery_date: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Currency</label>
              <input value={formData.currency} onChange={(event) => setFormData({ ...formData, currency: event.target.value.toUpperCase() })} maxLength={10} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Notes</label>
              <textarea value={formData.notes || ''} onChange={(event) => setFormData({ ...formData, notes: event.target.value })} rows={3} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Order Items</h2>
            <button onClick={addLine} className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30">
              <Plus className="w-4 h-4" />
              Add Line
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Item</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Available</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Qty</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Unit Price</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Tax %</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Discount</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {formData.items.map((line, index) => {
                  const selectedItem = itemsById.get(Number(line.item_id))
                  return (
                    <tr key={index}>
                      <td className="px-4 py-3 min-w-72">
                        <select value={line.item_id || ''} onChange={(event) => handleItemChange(index, Number(event.target.value))} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                          <option value="">Select item</option>
                          {items.map((item) => <option key={item.id} value={item.id}>{item.item_code} - {item.name}</option>)}
                        </select>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">{selectedItem ? `${selectedItem.quantity} ${selectedItem.unit_of_measure}` : '-'}</td>
                      <td className="px-4 py-3">
                        <input type="number" step="0.01" min="0" value={line.ordered_quantity} onChange={(event) => updateLine(index, { ordered_quantity: Number(event.target.value) })} className="w-24 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                      </td>
                      <td className="px-4 py-3">
                        <input type="number" step="0.01" min="0" value={line.unit_price} onChange={(event) => updateLine(index, { unit_price: Number(event.target.value) })} className="w-28 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                      </td>
                      <td className="px-4 py-3">
                        <input type="number" step="0.01" min="0" value={line.tax_rate || 0} onChange={(event) => updateLine(index, { tax_rate: Number(event.target.value) })} className="w-24 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                      </td>
                      <td className="px-4 py-3">
                        <input type="number" step="0.01" min="0" value={line.discount_amount || 0} onChange={(event) => updateLine(index, { discount_amount: Number(event.target.value) })} className="w-28 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                      </td>
                      <td className="px-4 py-3 text-right text-sm font-medium text-gray-900 dark:text-gray-100">{lineTotal(line).toFixed(2)}</td>
                      <td className="px-4 py-3 text-right">
                        <button onClick={() => removeLine(index)} disabled={formData.items.length === 1} className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 disabled:opacity-40">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <div className="px-4 sm:px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
            <div className="w-full max-w-sm space-y-2 text-sm">
              <div className="flex justify-between text-gray-700 dark:text-gray-300"><span>Subtotal</span><span>{totals.subtotal.toFixed(2)}</span></div>
              <div className="flex justify-between text-gray-700 dark:text-gray-300"><span>Tax</span><span>{totals.tax.toFixed(2)}</span></div>
              <div className="flex justify-between text-gray-700 dark:text-gray-300"><span>Discount</span><span>{totals.discount.toFixed(2)}</span></div>
              <div className="flex justify-between text-base font-semibold text-gray-900 dark:text-gray-100 border-t border-gray-200 dark:border-gray-700 pt-2"><span>Total</span><span>{totals.total.toFixed(2)} {formData.currency}</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SalesOrderFormPage
