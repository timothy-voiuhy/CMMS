import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import {
  inventoryService,
  type CreateInventoryItemRequest,
  type InventoryCategory,
  type InventoryCategoryTree,
} from '../../services/inventory.service'

const InventoryFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditMode = id && id !== 'new'

  const [formData, setFormData] = useState<CreateInventoryItemRequest>({
    item_code: '',
    name: '',
    description: '',
    category_id: 0,
    unit_of_measure: '',
    quantity: 0,
    min_quantity: undefined,
    max_quantity: undefined,
    reorder_point: undefined,
    unit_cost: undefined,
    location: '',
    supplier: '',
    batch_number: '',
    expiry_date: '',
    notes: '',
  })
  const [categories, setCategories] = useState<InventoryCategory[]>([])
  const [categoryTree, setCategoryTree] = useState<InventoryCategoryTree[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadCategories()
    if (isEditMode) {
      loadItem()
    }
  }, [id])

  const loadCategories = async () => {
    try {
      const [flatCategories, tree] = await Promise.all([
        inventoryService.getCategories(),
        inventoryService.getCategoryTree(),
      ])
      setCategories(flatCategories)
      setCategoryTree(tree)
      
      // Set default category if creating new item
      if (!isEditMode && flatCategories.length > 0) {
        setFormData((prev) => ({ ...prev, category_id: flatCategories[0].id }))
      }
    } catch (error) {
      console.error('Failed to load categories:', error)
    }
  }

  const loadItem = async () => {
    if (!id || id === 'new') return

    try {
      setIsLoading(true)
      const item = await inventoryService.getById(parseInt(id))
      setFormData({
        item_code: item.item_code,
        name: item.name,
        description: item.description || '',
        category_id: item.category_id,
        unit_of_measure: item.unit_of_measure,
        quantity: item.quantity,
        min_quantity: item.min_quantity,
        max_quantity: item.max_quantity,
        reorder_point: item.reorder_point,
        unit_cost: item.unit_cost,
        location: item.location || '',
        supplier: item.supplier || '',
        batch_number: item.batch_number || '',
        expiry_date: item.expiry_date || '',
        notes: item.notes || '',
      })
    } catch (error) {
      console.error('Failed to load item:', error)
      setError('Failed to load item details')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSaving(true)

    try {
      if (isEditMode) {
        const { item_code, quantity, ...updateData } = formData
        await inventoryService.update(parseInt(id), updateData)
      } else {
        await inventoryService.create(formData)
      }
      navigate('/inventory')
    } catch (error: any) {
      console.error('Failed to save item:', error)
      const detail = error.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((e: any) => e.msg || e.message).join(', '))
      } else if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError('Failed to save item')
      }
    } finally {
      setIsSaving(false)
    }
  }

  const handleChange = (field: keyof CreateInventoryItemRequest, value: any) => {
    setFormData({ ...formData, [field]: value })
  }

  // Render category options with indentation for hierarchy
  const renderCategoryOptions = (
    categories: InventoryCategoryTree[],
    level: number = 0
  ): React.ReactNode => {
    return categories.map((category) => (
      <React.Fragment key={category.id}>
        <option value={category.id}>
          {'\u00A0'.repeat(level * 4)}{category.name}
        </option>
        {category.children && category.children.length > 0 &&
          renderCategoryOptions(category.children, level + 1)}
      </React.Fragment>
    ))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/inventory')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Inventory
        </button>
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          {isEditMode ? 'Edit Inventory Item' : 'Add New Inventory Item'}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          {isEditMode ? 'Update inventory item information' : 'Add a new item to inventory'}
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="space-y-4 sm:space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Item Code <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.item_code}
                  onChange={(e) => handleChange('item_code', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="e.g., ITM-001"
                  disabled={isEditMode}
                />
                {isEditMode && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Item code cannot be changed</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Item Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="e.g., Steel Plate"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Item description..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.category_id}
                  onChange={(e) => handleChange('category_id', parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="">Select a category</option>
                  {renderCategoryOptions(categoryTree)}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Unit of Measure <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.unit_of_measure}
                  onChange={(e) => handleChange('unit_of_measure', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="e.g., kg, pcs, liters"
                />
              </div>
            </div>
          </div>

          {/* Quantity & Stock Levels */}
          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Quantity & Stock Levels</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Initial Quantity {!isEditMode && <span className="text-red-500">*</span>}
                </label>
                <input
                  type="number"
                  step="0.01"
                  required={!isEditMode}
                  value={formData.quantity}
                  onChange={(e) => handleChange('quantity', parseFloat(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  disabled={isEditMode}
                />
                {isEditMode && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Use transaction history to adjust quantity
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Reorder Point</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.reorder_point || ''}
                  onChange={(e) =>
                    handleChange('reorder_point', e.target.value ? parseFloat(e.target.value) : undefined)
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Minimum quantity before reorder"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Minimum Quantity</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.min_quantity || ''}
                  onChange={(e) =>
                    handleChange('min_quantity', e.target.value ? parseFloat(e.target.value) : undefined)
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Maximum Quantity</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.max_quantity || ''}
                  onChange={(e) =>
                    handleChange('max_quantity', e.target.value ? parseFloat(e.target.value) : undefined)
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
            </div>
          </div>

          {/* Costing & Location */}
          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Costing & Location</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Unit Cost</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.unit_cost || ''}
                  onChange={(e) =>
                    handleChange('unit_cost', e.target.value ? parseFloat(e.target.value) : undefined)
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Cost per unit"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleChange('location', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="e.g., Warehouse A, Shelf 5"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Supplier</label>
                <input
                  type="text"
                  value={formData.supplier}
                  onChange={(e) => handleChange('supplier', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Supplier name"
                />
              </div>
            </div>
          </div>

          {/* Batch Tracking */}
          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Batch Tracking (Optional)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Batch Number</label>
                <input
                  type="text"
                  value={formData.batch_number}
                  onChange={(e) => handleChange('batch_number', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Batch or lot number"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Expiry Date</label>
                <input
                  type="date"
                  value={formData.expiry_date}
                  onChange={(e) => handleChange('expiry_date', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                />
              </div>
            </div>
          </div>

          {/* Notes */}
          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Additional Notes</h2>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
              placeholder="Additional notes or comments..."
            />
          </div>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-1 gap-3 sm:flex sm:justify-end sm:gap-4 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={() => navigate('/inventory')}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSaving}
            className="px-6 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 flex items-center gap-2 disabled:opacity-50"
          >
            {isSaving ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                {isEditMode ? 'Update Item' : 'Create Item'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default InventoryFormPage
