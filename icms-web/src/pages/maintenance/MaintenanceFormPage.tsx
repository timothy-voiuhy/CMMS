import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import {
  maintenanceService,
  type CreateMaintenanceReportRequest,
} from '../../services/maintenance.service'
import { equipmentService } from '../../services/equipment.service'
import { craftsmanService } from '../../services/craftsman.service'
import { workOrderService, type WorkOrder } from '../../services/workOrder.service'

const MaintenanceFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditMode = Boolean(id && id !== 'new')

  const [formData, setFormData] = useState<CreateMaintenanceReportRequest>({
    work_order_id: 0,
    equipment_id: 0,
    craftsman_id: 0,
    work_performed: '',
    findings: '',
    recommendations: '',
    parts_used: '',
    labor_hours: undefined,
    equipment_operational: true,
    follow_up_required: false,
  })
  const [equipment, setEquipment] = useState<any[]>([])
  const [craftsmen, setCraftsmen] = useState<any[]>([])
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadEquipment()
    loadCraftsmen()
    loadWorkOrders()
    if (isEditMode) {
      loadReport()
    }
  }, [id])

  const loadEquipment = async () => {
    try {
      const response = await equipmentService.getAll({ limit: 100 })
      setEquipment(response.data)
    } catch (error) {
      console.error('Failed to load equipment:', error)
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

  const loadWorkOrders = async () => {
    try {
      const response = await workOrderService.getAll({ limit: 100 })
      setWorkOrders(response.data)
    } catch (error) {
      console.error('Failed to load work orders:', error)
    }
  }

  const loadReport = async () => {
    if (!id || id === 'new') return

    try {
      setIsLoading(true)
      const report = await maintenanceService.getById(parseInt(id))
      setFormData({
        work_order_id: report.work_order_id,
        equipment_id: report.equipment_id,
        craftsman_id: report.craftsman_id,
        work_performed: report.work_performed,
        findings: report.findings || '',
        recommendations: report.recommendations || '',
        parts_used: report.parts_used || '',
        labor_hours: report.labor_hours,
        equipment_operational: report.equipment_operational,
        follow_up_required: report.follow_up_required,
      })
    } catch (error) {
      console.error('Failed to load report:', error)
      setError('Failed to load report details')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    if (!formData.equipment_id || formData.equipment_id === 0) {
      setError('Please select an equipment')
      return
    }
    if (!formData.work_order_id || formData.work_order_id === 0) {
      setError('Please select a work order')
      return
    }
    if (!formData.craftsman_id || formData.craftsman_id === 0) {
      setError('Please select a craftsman')
      return
    }

    setIsSaving(true)

    try {
      if (isEditMode) {
        const { work_order_id, equipment_id, craftsman_id, ...updateData } = formData
        await maintenanceService.update(parseInt(id!), updateData)
      } else {
        await maintenanceService.create(formData)
      }
      navigate('/maintenance')
    } catch (error: any) {
      console.error('Failed to save report:', error)
      const detail = error.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((e: any) => e.msg || e.message).join(', '))
      } else if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError('Failed to save report')
      }
    } finally {
      setIsSaving(false)
    }
  }

  const handleChange = (field: keyof CreateMaintenanceReportRequest, value: any) => {
    setFormData({ ...formData, [field]: value })
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
          onClick={() => navigate('/maintenance')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Maintenance Reports
        </button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          {isEditMode ? 'Edit Maintenance Report' : 'Create Maintenance Report'}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          {isEditMode ? 'Update maintenance report information' : 'Document maintenance work performed'}
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="space-y-4 sm:space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Equipment <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.equipment_id}
                  onChange={(e) => handleChange('equipment_id', parseInt(e.target.value))}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isEditMode}
                >
                  <option value="0">Select equipment...</option>
                  {equipment.map((eq) => (
                    <option key={eq.id} value={eq.id}>
                      {eq.name} ({eq.equipment_id})
                    </option>
                  ))}
                </select>
                {isEditMode && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Equipment cannot be changed</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Craftsman <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.craftsman_id}
                  onChange={(e) => handleChange('craftsman_id', parseInt(e.target.value))}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isEditMode}
                >
                  <option value="0">Select craftsman...</option>
                  {craftsmen.map((craftsman) => (
                    <option key={craftsman.id} value={craftsman.id}>
                      {craftsman.full_name} ({craftsman.employee_id})
                    </option>
                  ))}
                </select>
                {isEditMode && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Craftsman cannot be changed</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Work Order ID <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.work_order_id || 0}
                  onChange={(e) => handleChange('work_order_id', parseInt(e.target.value) || 0)}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isEditMode}
                >
                  <option value={0}>Select work order...</option>
                  {workOrders.map((workOrder) => (
                    <option key={workOrder.id} value={workOrder.id}>
                      {workOrder.work_order_number} — {workOrder.title}
                    </option>
                  ))}
                </select>
                {!isEditMode && workOrders.length === 0 && (
                  <p className="text-xs text-red-600 dark:text-red-400 mt-1">No work orders are available. Create a work order first.</p>
                )}
                {isEditMode && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Work order cannot be changed</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Labor Hours</label>
                <input
                  type="number"
                  step="0.5"
                  value={formData.labor_hours || ''}
                  onChange={(e) =>
                    handleChange('labor_hours', e.target.value ? parseFloat(e.target.value) : undefined)
                  }
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Hours spent"
                />
              </div>
            </div>
          </div>

          {/* Work Details */}
          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Work Details</h2>
            <div className="space-y-4 sm:space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Work Performed <span className="text-red-500">*</span>
                </label>
                <textarea
                  required
                  value={formData.work_performed}
                  onChange={(e) => handleChange('work_performed', e.target.value)}
                  rows={4}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe the maintenance work performed..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Findings</label>
                <textarea
                  value={formData.findings}
                  onChange={(e) => handleChange('findings', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Any findings, issues, or observations..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recommendations</label>
                <textarea
                  value={formData.recommendations}
                  onChange={(e) => handleChange('recommendations', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Recommendations for future maintenance..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Parts Used</label>
                <textarea
                  value={formData.parts_used}
                  onChange={(e) => handleChange('parts_used', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="List of parts and materials used..."
                />
              </div>
            </div>
          </div>

          {/* Status */}
          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Status</h2>
            <div className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.equipment_operational}
                  onChange={(e) => handleChange('equipment_operational', e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Equipment Operational</span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Check if equipment is operational after maintenance</p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.follow_up_required}
                  onChange={(e) => handleChange('follow_up_required', e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">Follow-up Required</span>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Check if additional work or inspection is needed</p>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-1 gap-3 sm:flex sm:justify-end sm:gap-4 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={() => navigate('/maintenance')}
            className="px-6 py-2 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
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
                {isEditMode ? 'Update Report' : 'Create Report'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default MaintenanceFormPage
