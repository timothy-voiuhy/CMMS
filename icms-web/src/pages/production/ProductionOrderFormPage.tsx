import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save, Loader } from 'lucide-react'
import {
  productionOrderService,
  productionLineService,
  type ProductionOrder,
  type CreateProductionOrderRequest,
  type UpdateProductionOrderRequest,
  type ProductionOrderStatus,
  type ProductionLine,
} from '../../services/production.service'

const ProductionOrderFormPage: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEdit = id && id !== 'new'
  
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [productionLines, setProductionLines] = useState<ProductionLine[]>([])
  const [formData, setFormData] = useState<CreateProductionOrderRequest & { status?: ProductionOrderStatus; produced_quantity?: number }>({
    production_line_id: 0,
    product_name: '',
    product_code: '',
    target_quantity: 0,
    unit: '',
    priority: 3,
    scheduled_start: '',
    scheduled_end: '',
    notes: '',
  })

  useEffect(() => {
    loadProductionLines()
    if (isEdit) {
      loadOrder()
    }
  }, [id])

  const loadProductionLines = async () => {
    try {
      const response = await productionLineService.getAll({ limit: 100 })
      setProductionLines(response.data)
    } catch (error) {
      console.error('Failed to load production lines:', error)
    }
  }

  const loadOrder = async () => {
    if (!id || id === 'new') return
    
    try {
      setIsLoading(true)
      const order = await productionOrderService.getById(parseInt(id))
      setFormData({
        production_line_id: order.production_line_id,
        product_name: order.product_name,
        product_code: order.product_code || '',
        target_quantity: order.target_quantity,
        unit: order.unit,
        priority: order.priority,
        scheduled_start: order.scheduled_start || '',
        scheduled_end: order.scheduled_end || '',
        notes: order.notes || '',
        status: order.status,
        produced_quantity: order.produced_quantity,
      })
    } catch (error) {
      console.error('Failed to load production order:', error)
      alert('Failed to load production order')
      navigate('/production/orders')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.product_name || !formData.production_line_id || !formData.target_quantity || !formData.unit) {
      alert('Please fill in all required fields')
      return
    }

    try {
      setIsSaving(true)
      
      if (isEdit && id) {
        const updateData: UpdateProductionOrderRequest = {
          product_name: formData.product_name,
          product_code: formData.product_code || undefined,
          target_quantity: formData.target_quantity,
          unit: formData.unit,
          priority: formData.priority,
          scheduled_start: formData.scheduled_start || undefined,
          scheduled_end: formData.scheduled_end || undefined,
          notes: formData.notes || undefined,
          status: formData.status,
          produced_quantity: formData.produced_quantity,
        }
        await productionOrderService.update(parseInt(id), updateData)
      } else {
        await productionOrderService.create(formData)
      }
      
      navigate('/production/orders')
    } catch (error) {
      console.error('Failed to save production order:', error)
      alert('Failed to save production order')
    } finally {
      setIsSaving(false)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/production/orders')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Production Orders
        </button>
        <h1 className="text-2xl font-bold text-gray-800">
          {isEdit ? 'Edit Production Order' : 'New Production Order'}
        </h1>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Production Line <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.production_line_id}
                  onChange={(e) => handleChange('production_line_id', parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value={0}>Select Production Line</option>
                  {productionLines.map((line) => (
                    <option key={line.id} value={line.id}>
                      {line.name} ({line.line_code})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => handleChange('priority', parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={1}>1 - Urgent</option>
                  <option value={2}>2 - High</option>
                  <option value={3}>3 - Normal</option>
                  <option value={4}>4 - Low</option>
                  <option value={5}>5 - Very Low</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.product_name}
                  onChange={(e) => handleChange('product_name', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Product Name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Code
                </label>
                <input
                  type="text"
                  value={formData.product_code}
                  onChange={(e) => handleChange('product_code', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="SKU or Product Code"
                />
              </div>
              {isEdit && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => handleChange('status', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="paused">Paused</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
              )}
            </div>
          </div>

          {/* Quantity */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Quantity</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Quantity <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.target_quantity}
                  onChange={(e) => handleChange('target_quantity', parseFloat(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="1000"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Unit <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.unit}
                  onChange={(e) => handleChange('unit', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="pcs, kg, liters, etc."
                  required
                />
              </div>
              {isEdit && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Produced Quantity
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.produced_quantity || 0}
                    onChange={(e) => handleChange('produced_quantity', parseFloat(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Schedule */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Schedule</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Scheduled Start
                </label>
                <input
                  type="datetime-local"
                  value={formData.scheduled_start}
                  onChange={(e) => handleChange('scheduled_start', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Scheduled End
                </label>
                <input
                  type="datetime-local"
                  value={formData.scheduled_end}
                  onChange={(e) => handleChange('scheduled_end', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Notes</h2>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
              placeholder="Additional notes or instructions..."
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={() => navigate('/production/orders')}
              className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="flex items-center gap-2 px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isSaving ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  {isEdit ? 'Update' : 'Create'} Order
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProductionOrderFormPage
