import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Plus, Save, Send, Trash2 } from 'lucide-react'
import {
  inventoryService,
  type CreateInventoryRequisitionLine,
  type CreateInventoryRequisitionRequest,
  type InventoryItem,
  type RequisitionApprover,
  type RequisitionPriority,
} from '../../services/inventory.service'

const emptyLine = (): CreateInventoryRequisitionLine => ({
  item_id: 0,
  requested_quantity: 1,
  notes: '',
})

const InventoryRequisitionFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditMode = Boolean(id)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [items, setItems] = useState<InventoryItem[]>([])
  const [approvers, setApprovers] = useState<RequisitionApprover[]>([])
  const [formData, setFormData] = useState<CreateInventoryRequisitionRequest>({
    title: '',
    description: '',
    priority: 'medium',
    needed_by: '',
    department: '',
    notes: '',
    items: [emptyLine()],
  })

  const itemsById = useMemo(() => {
    return new Map(items.map((item) => [item.id, item]))
  }, [items])

  useEffect(() => {
    loadInventoryItems()
    loadApprovers()
  }, [])

  useEffect(() => {
    if (isEditMode) {
      loadRequisition()
    }
  }, [id])

  const loadInventoryItems = async () => {
    try {
      const response = await inventoryService.getAll({ limit: 100 })
      setItems(response.data)
    } catch (error) {
      console.error('Failed to load inventory items:', error)
    }
  }

  const loadApprovers = async () => {
    try {
      setApprovers(await inventoryService.getRequisitionApprovers())
    } catch (error) {
      console.error('Failed to load requisition approvers:', error)
    }
  }

  const loadRequisition = async () => {
    if (!id) return

    try {
      setIsLoading(true)
      const requisition = await inventoryService.getRequisitionById(parseInt(id))
      if (requisition.status !== 'draft') {
        alert('Only draft requisitions can be edited')
        navigate(`/inventory/requisitions/${id}`)
        return
      }
      setFormData({
        title: requisition.title,
        description: requisition.description || '',
        priority: requisition.priority,
        needed_by: requisition.needed_by || '',
        department: requisition.department || '',
        work_order_id: requisition.work_order_id,
        production_order_id: requisition.production_order_id,
        approver_id: requisition.approver_id,
        notes: requisition.notes || '',
        items: (requisition.items || []).map((line) => ({
          item_id: line.item_id,
          requested_quantity: line.requested_quantity,
          notes: line.notes || '',
        })),
      })
    } catch (error) {
      console.error('Failed to load requisition:', error)
      alert('Failed to load requisition')
      navigate('/inventory/requisitions')
    } finally {
      setIsLoading(false)
    }
  }

  const updateLine = (index: number, patch: Partial<CreateInventoryRequisitionLine>) => {
    const nextLines = [...formData.items]
    nextLines[index] = { ...nextLines[index], ...patch }
    setFormData({ ...formData, items: nextLines })
  }

  const addLine = () => {
    setFormData({ ...formData, items: [...formData.items, emptyLine()] })
  }

  const removeLine = (index: number) => {
    if (formData.items.length === 1) return
    setFormData({ ...formData, items: formData.items.filter((_, lineIndex) => lineIndex !== index) })
  }

  const buildPayload = (): CreateInventoryRequisitionRequest => ({
    ...formData,
    description: formData.description || undefined,
    needed_by: formData.needed_by || undefined,
    department: formData.department || undefined,
    notes: formData.notes || undefined,
    work_order_id: formData.work_order_id || undefined,
    production_order_id: formData.production_order_id || undefined,
    approver_id: formData.approver_id || undefined,
    items: formData.items.map((line) => ({
      item_id: Number(line.item_id),
      requested_quantity: Number(line.requested_quantity),
      notes: line.notes || undefined,
    })),
  })

  const validate = () => {
    if (!formData.title.trim()) {
      alert('Title is required')
      return false
    }
    if (formData.items.length === 0) {
      alert('Add at least one item')
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
      if (!line.requested_quantity || line.requested_quantity <= 0) {
        alert('Every line quantity must be greater than zero')
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
        return await inventoryService.updateRequisition(parseInt(id), buildPayload())
      }
      return await inventoryService.createRequisition(buildPayload())
    } catch (error: any) {
      console.error('Failed to save requisition:', error)
      const detail = error.response?.data?.detail
      alert(typeof detail === 'string' ? detail : 'Failed to save requisition')
      return null
    } finally {
      setIsSaving(false)
    }
  }

  const handleSave = async () => {
    const requisition = await saveDraft()
    if (requisition) {
      navigate(`/inventory/requisitions/${requisition.id}`)
    }
  }

  const handleSubmit = async () => {
    if (!formData.approver_id) {
      alert('Select an approver before submitting')
      return
    }
    const requisition = await saveDraft()
    if (!requisition) return

    try {
      setIsSaving(true)
      const submitted = await inventoryService.submitRequisitionWithApprover(requisition.id, formData.approver_id)
      navigate(`/inventory/requisitions/${submitted.id}`)
    } catch (error: any) {
      console.error('Failed to submit requisition:', error)
      const detail = error.response?.data?.detail
      alert(typeof detail === 'string' ? detail : 'Failed to submit requisition')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

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
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              {isEditMode ? 'Edit Requisition' : 'New Requisition'}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Prepare an inventory request before approval and issue</p>
          </div>
          <div className="grid grid-cols-1 gap-2 sm:flex sm:items-center sm:gap-3">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              Save Draft
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSaving}
              className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              Submit
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(event) => setFormData({ ...formData, title: event.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Request title"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Approver
              </label>
              <select
                value={formData.approver_id || ''}
                onChange={(event) => setFormData({ ...formData, approver_id: event.target.value ? parseInt(event.target.value) : undefined })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select an authorized approver</option>
                {approvers.map((approver) => (
                  <option key={approver.id} value={approver.id}>{approver.full_name} ({approver.username})</option>
                ))}
              </select>
              {approvers.length === 0 && <p className="mt-1 text-sm text-red-600 dark:text-red-400">No authorized approvers are available.</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Priority</label>
              <select
                value={formData.priority}
                onChange={(event) => setFormData({ ...formData, priority: event.target.value as RequisitionPriority })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Needed By</label>
              <input
                type="date"
                value={formData.needed_by}
                onChange={(event) => setFormData({ ...formData, needed_by: event.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Department</label>
              <input
                type="text"
                value={formData.department}
                onChange={(event) => setFormData({ ...formData, department: event.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Maintenance, Production, Quality..."
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Work Order ID</label>
                <input
                  type="number"
                  value={formData.work_order_id || ''}
                  onChange={(event) => setFormData({ ...formData, work_order_id: event.target.value ? parseInt(event.target.value) : undefined })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Production Order ID</label>
                <input
                  type="number"
                  value={formData.production_order_id || ''}
                  onChange={(event) => setFormData({ ...formData, production_order_id: event.target.value ? parseInt(event.target.value) : undefined })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(event) => setFormData({ ...formData, description: event.target.value })}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Request context"
              />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Requested Items</h2>
            <button
              onClick={addLine}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30"
            >
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
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Quantity</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Notes</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {formData.items.map((line, index) => {
                  const selectedItem = itemsById.get(Number(line.item_id))
                  return (
                    <tr key={index}>
                      <td className="px-4 py-3 min-w-72">
                        <select
                          value={line.item_id || ''}
                          onChange={(event) => updateLine(index, { item_id: parseInt(event.target.value) || 0 })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Select item</option>
                          {items.map((item) => (
                            <option key={item.id} value={item.id}>
                              {item.item_code} - {item.name}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                        {selectedItem ? `${selectedItem.quantity} ${selectedItem.unit_of_measure}` : '-'}
                      </td>
                      <td className="px-4 py-3 w-40">
                        <input
                          type="number"
                          step="0.01"
                          value={line.requested_quantity}
                          onChange={(event) => updateLine(index, { requested_quantity: parseFloat(event.target.value) || 0 })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-4 py-3 min-w-64">
                        <input
                          type="text"
                          value={line.notes || ''}
                          onChange={(event) => updateLine(index, { notes: event.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Line notes"
                        />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => removeLine(index)}
                          disabled={formData.items.length === 1}
                          className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 disabled:opacity-40"
                          title="Remove line"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Notes</label>
          <textarea
            value={formData.notes}
            onChange={(event) => setFormData({ ...formData, notes: event.target.value })}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Internal notes"
          />
        </div>
      </div>
    </div>
  )
}

export default InventoryRequisitionFormPage
