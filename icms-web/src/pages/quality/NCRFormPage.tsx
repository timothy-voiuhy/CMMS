import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save, Loader } from 'lucide-react'
import {
  qualityService,
  type CreateNCRRequest,
  type UpdateNCRRequest,
  type NCRSeverity,
  type NCRStatus,
} from '../../services/quality.service'
import { useAuthStore } from '../../store/authStore'

const NCRFormPage: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEdit = id && id !== 'new'
  const { user } = useAuthStore()

  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [formData, setFormData] = useState<CreateNCRRequest & { status?: NCRStatus }>({
    title: '',
    description: '',
    severity: 'minor',
    reported_by_id: user?.id || 0,
    inspection_id: undefined,
    production_order_id: undefined,
    equipment_id: undefined,
    batch_number: '',
    assigned_to_id: undefined,
    root_cause: '',
    corrective_action: '',
    preventive_action: '',
    estimated_cost: undefined,
  })

  useEffect(() => {
    if (isEdit) {
      loadNCR()
    }
  }, [id])

  const loadNCR = async () => {
    if (!id || id === 'new') return

    try {
      setIsLoading(true)
      const ncr = await qualityService.getNCRById(parseInt(id))
      setFormData({
        title: ncr.title,
        description: ncr.description,
        severity: ncr.severity,
        reported_by_id: ncr.reported_by_id,
        inspection_id: ncr.inspection_id,
        production_order_id: ncr.production_order_id,
        equipment_id: ncr.equipment_id,
        batch_number: ncr.batch_number || '',
        assigned_to_id: ncr.assigned_to_id,
        root_cause: ncr.root_cause || '',
        corrective_action: ncr.corrective_action || '',
        preventive_action: ncr.preventive_action || '',
        estimated_cost: ncr.estimated_cost,
        status: ncr.status,
      })
    } catch (error) {
      console.error('Failed to load NCR:', error)
      alert('Failed to load NCR')
      navigate('/quality')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title || !formData.description) {
      alert('Please fill in all required fields')
      return
    }

    try {
      setIsSaving(true)

      if (isEdit && id) {
        const updateData: UpdateNCRRequest = {
          title: formData.title,
          description: formData.description,
          severity: formData.severity,
          inspection_id: formData.inspection_id,
          production_order_id: formData.production_order_id,
          equipment_id: formData.equipment_id,
          batch_number: formData.batch_number || undefined,
          assigned_to_id: formData.assigned_to_id,
          root_cause: formData.root_cause || undefined,
          corrective_action: formData.corrective_action || undefined,
          preventive_action: formData.preventive_action || undefined,
          estimated_cost: formData.estimated_cost,
          status: formData.status,
        }
        await qualityService.updateNCR(parseInt(id), updateData)
      } else {
        await qualityService.createNCR(formData)
      }

      navigate('/quality')
    } catch (error) {
      console.error('Failed to save NCR:', error)
      alert('Failed to save NCR')
    } finally {
      setIsSaving(false)
    }
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
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
          {isEdit ? 'Edit Non-Conformance Report' : 'New Non-Conformance Report'}
        </h1>
      </div>

      {/* Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Brief title describing the non-conformance"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Severity <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.severity}
                  onChange={(e) => handleChange('severity', e.target.value as NCRSeverity)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  required
                >
                  <option value="minor">Minor</option>
                  <option value="major">Major</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              {isEdit && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => handleChange('status', e.target.value as NCRStatus)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="open">Open</option>
                    <option value="investigating">Investigating</option>
                    <option value="corrective_action">Corrective Action</option>
                    <option value="closed">Closed</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Batch Number
                </label>
                <input
                  type="text"
                  value={formData.batch_number}
                  onChange={(e) => handleChange('batch_number', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Related batch number"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Estimated Cost
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.estimated_cost || ''}
                  onChange={(e) => handleChange('estimated_cost', e.target.value ? parseFloat(e.target.value) : undefined)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Estimated cost impact"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  rows={4}
                  placeholder="Detailed description of the non-conformance..."
                  required
                />
              </div>
            </div>
          </div>

          {/* Analysis & Actions */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Analysis & Actions</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Root Cause Analysis
                </label>
                <textarea
                  value={formData.root_cause}
                  onChange={(e) => handleChange('root_cause', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  rows={3}
                  placeholder="Identified root cause of the issue..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Corrective Action
                </label>
                <textarea
                  value={formData.corrective_action}
                  onChange={(e) => handleChange('corrective_action', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  rows={3}
                  placeholder="Actions taken to correct the issue..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Preventive Action
                </label>
                <textarea
                  value={formData.preventive_action}
                  onChange={(e) => handleChange('preventive_action', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  rows={3}
                  placeholder="Actions to prevent recurrence..."
                />
              </div>
            </div>
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
                  {isEdit ? 'Update' : 'Create'} NCR
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default NCRFormPage
