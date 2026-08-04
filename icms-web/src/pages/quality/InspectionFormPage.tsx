import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save, Plus, Trash2, Loader } from 'lucide-react'
import {
  qualityService,
  type CreateInspectionRequest,
  type UpdateInspectionRequest,
  type QualityInspectionItem,
  type InspectionResult,
  type InspectionStatus,
} from '../../services/quality.service'
import { useAuthStore } from '../../store/authStore'

const InspectionFormPage: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEdit = id && id !== 'new'
  const { user } = useAuthStore()

  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [formData, setFormData] = useState<CreateInspectionRequest & { status?: InspectionStatus; result?: InspectionResult }>({
    product_name: '',
    inspection_type: 'incoming',
    inspection_date: new Date().toISOString().slice(0, 16),
    inspector_id: user?.id || 0,
    sample_size: undefined,
    batch_number: '',
    production_order_id: undefined,
    specifications: '',
    observations: '',
    notes: '',
    inspection_items: [],
  })

  useEffect(() => {
    if (isEdit) {
      loadInspection()
    }
  }, [id])

  const loadInspection = async () => {
    if (!id || id === 'new') return

    try {
      setIsLoading(true)
      const inspection = await qualityService.getInspectionById(parseInt(id))
      setFormData({
        product_name: inspection.product_name,
        inspection_type: inspection.inspection_type,
        inspection_date: inspection.inspection_date,
        inspector_id: inspection.inspector_id,
        sample_size: inspection.sample_size,
        batch_number: inspection.batch_number || '',
        production_order_id: inspection.production_order_id,
        specifications: inspection.specifications || '',
        observations: inspection.observations || '',
        notes: inspection.notes || '',
        status: inspection.status,
        result: inspection.result,
        inspection_items: inspection.inspection_items.map(item => ({
          checkpoint_name: item.checkpoint_name,
          specification: item.specification || '',
          measured_value: item.measured_value || '',
          result: item.result,
          notes: item.notes || '',
        })),
      })
    } catch (error) {
      console.error('Failed to load inspection:', error)
      alert('Failed to load inspection')
      navigate('/quality')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.product_name || !formData.inspection_type) {
      alert('Please fill in all required fields')
      return
    }

    try {
      setIsSaving(true)

      if (isEdit && id) {
        const updateData: UpdateInspectionRequest = {
          product_name: formData.product_name,
          inspection_type: formData.inspection_type,
          inspection_date: formData.inspection_date,
          sample_size: formData.sample_size,
          batch_number: formData.batch_number || undefined,
          production_order_id: formData.production_order_id,
          specifications: formData.specifications || undefined,
          observations: formData.observations || undefined,
          notes: formData.notes || undefined,
          status: formData.status,
          result: formData.result,
        }
        await qualityService.updateInspection(parseInt(id), updateData)
      } else {
        await qualityService.createInspection(formData)
      }

      navigate('/quality')
    } catch (error) {
      console.error('Failed to save inspection:', error)
      alert('Failed to save inspection')
    } finally {
      setIsSaving(false)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const addInspectionItem = () => {
    setFormData(prev => ({
      ...prev,
      inspection_items: [
        ...prev.inspection_items,
        {
          checkpoint_name: '',
          specification: '',
          measured_value: '',
          result: 'pending' as InspectionResult,
          notes: '',
        },
      ],
    }))
  }

  const updateInspectionItem = (index: number, field: keyof QualityInspectionItem, value: any) => {
    setFormData(prev => ({
      ...prev,
      inspection_items: prev.inspection_items.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      ),
    }))
  }

  const removeInspectionItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      inspection_items: prev.inspection_items.filter((_, i) => i !== index),
    }))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-400" />
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/quality')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Quality Control
        </button>
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          {isEdit ? 'Edit Inspection' : 'New Quality Inspection'}
        </h1>
      </div>

      {/* Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Product Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.product_name}
                  onChange={(e) => handleChange('product_name', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Product name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Inspection Type <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.inspection_type}
                  onChange={(e) => handleChange('inspection_type', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  required
                >
                  <option value="incoming">Incoming</option>
                  <option value="in_process">In-Process</option>
                  <option value="final">Final</option>
                  <option value="random">Random</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Inspection Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="datetime-local"
                  value={formData.inspection_date}
                  onChange={(e) => handleChange('inspection_date', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Sample Size
                </label>
                <input
                  type="number"
                  value={formData.sample_size || ''}
                  onChange={(e) => handleChange('sample_size', e.target.value ? parseInt(e.target.value) : undefined)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Number of samples"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Batch Number
                </label>
                <input
                  type="text"
                  value={formData.batch_number}
                  onChange={(e) => handleChange('batch_number', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Batch number"
                />
              </div>
              {isEdit && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
                    <select
                      value={formData.status}
                      onChange={(e) => handleChange('status', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                      <option value="failed">Failed</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Result</label>
                    <select
                      value={formData.result}
                      onChange={(e) => handleChange('result', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      <option value="pending">Pending</option>
                      <option value="pass">Pass</option>
                      <option value="fail">Fail</option>
                      <option value="conditional">Conditional</option>
                    </select>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Specifications */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Specifications & Notes</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Specifications
                </label>
                <textarea
                  value={formData.specifications}
                  onChange={(e) => handleChange('specifications', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  rows={3}
                  placeholder="Quality specifications and standards..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Observations
                </label>
                <textarea
                  value={formData.observations}
                  onChange={(e) => handleChange('observations', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  rows={3}
                  placeholder="Inspector observations..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Additional Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => handleChange('notes', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  rows={3}
                  placeholder="Additional notes..."
                />
              </div>
            </div>
          </div>

          {/* Inspection Items */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Inspection Checkpoints</h2>
              <button
                type="button"
                onClick={addInspectionItem}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
              >
                <Plus className="w-4 h-4" />
                Add Checkpoint
              </button>
            </div>
            {formData.inspection_items.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-gray-600 dark:text-gray-400">No checkpoints added yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {formData.inspection_items.map((item, index) => (
                  <div key={index} className="border border-gray-300 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50">
                    <div className="flex items-start justify-between mb-4">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Checkpoint {index + 1}</h3>
                      <button
                        type="button"
                        onClick={() => removeInspectionItem(index)}
                        className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Checkpoint Name
                        </label>
                        <input
                          type="text"
                          value={item.checkpoint_name}
                          onChange={(e) => updateInspectionItem(index, 'checkpoint_name', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                          placeholder="e.g., Dimension Check"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Result
                        </label>
                        <select
                          value={item.result}
                          onChange={(e) => updateInspectionItem(index, 'result', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                        >
                          <option value="pending">Pending</option>
                          <option value="pass">Pass</option>
                          <option value="fail">Fail</option>
                          <option value="conditional">Conditional</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Specification
                        </label>
                        <input
                          type="text"
                          value={item.specification || ''}
                          onChange={(e) => updateInspectionItem(index, 'specification', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                          placeholder="Expected value/range"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Measured Value
                        </label>
                        <input
                          type="text"
                          value={item.measured_value || ''}
                          onChange={(e) => updateInspectionItem(index, 'measured_value', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                          placeholder="Actual measured value"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Notes
                        </label>
                        <input
                          type="text"
                          value={item.notes || ''}
                          onChange={(e) => updateInspectionItem(index, 'notes', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                          placeholder="Additional notes for this checkpoint"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={() => navigate('/quality')}
              className="px-6 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="flex items-center gap-2 px-6 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
            >
              {isSaving ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  {isEdit ? 'Update' : 'Create'} Inspection
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default InspectionFormPage
