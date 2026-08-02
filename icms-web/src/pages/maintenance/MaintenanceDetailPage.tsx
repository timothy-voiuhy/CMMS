import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  FileText,
  Edit,
  Trash2,
  CheckCircle,
  AlertTriangle,
  Wrench,
  User,
  Calendar,
  Clock,
} from 'lucide-react'
import { maintenanceService, type MaintenanceReport } from '../../services/maintenance.service'

const MaintenanceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [report, setReport] = useState<MaintenanceReport | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isReviewing, setIsReviewing] = useState(false)

  useEffect(() => {
    if (id && id !== 'new') {
      loadReport()
    }
  }, [id])

  const loadReport = async () => {
    if (!id || id === 'new') return

    const reportId = parseInt(id)
    if (isNaN(reportId)) {
      navigate('/maintenance')
      return
    }

    try {
      setIsLoading(true)
      const data = await maintenanceService.getById(reportId)
      setReport(data)
    } catch (error) {
      console.error('Failed to load report:', error)
      alert('Failed to load report details')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!id || !report) return

    if (!confirm(`Are you sure you want to delete report ${report.report_number}?`)) return

    try {
      await maintenanceService.delete(parseInt(id))
      navigate('/maintenance')
    } catch (error) {
      console.error('Failed to delete report:', error)
      alert('Failed to delete report')
    }
  }

  const handleReview = async () => {
    if (!id) return

    try {
      setIsReviewing(true)
      await maintenanceService.review(parseInt(id))
      loadReport()
    } catch (error) {
      console.error('Failed to review report:', error)
      alert('Failed to review report')
    } finally {
      setIsReviewing(false)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-gray-500">Report not found</p>
          <button
            onClick={() => navigate('/maintenance')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Back to Maintenance Reports
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/maintenance')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-800 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Maintenance Reports
        </button>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 h-16 w-16 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Maintenance Report {report.report_number}
                </h1>
                <div className="flex items-center gap-4 mt-2">
                  {report.reviewed_by ? (
                    <span className="px-3 py-1 text-sm font-medium bg-green-100 text-green-800 rounded-full flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      Reviewed
                    </span>
                  ) : (
                    <span className="px-3 py-1 text-sm font-medium bg-yellow-100 text-yellow-800 rounded-full flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      Pending Review
                    </span>
                  )}
                  {report.follow_up_required && (
                    <span className="px-3 py-1 text-sm font-medium bg-orange-100 text-orange-800 rounded-full flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" />
                      Follow-up Required
                    </span>
                  )}
                  {!report.equipment_operational && (
                    <span className="px-3 py-1 text-sm font-medium bg-red-100 text-red-800 rounded-full flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" />
                      Not Operational
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {!report.reviewed_by && (
                <button
                  onClick={handleReview}
                  disabled={isReviewing}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 border border-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  {isReviewing ? 'Reviewing...' : 'Mark as Reviewed'}
                </button>
              )}
              <button
                onClick={() => navigate(`/maintenance/${id}/edit`)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={handleDelete}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-lg hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Info Cards */}
        <div className="space-y-6">
          {/* Basic Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Basic Information</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Wrench className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Equipment</p>
                  <p className="text-sm font-medium text-gray-900">Equipment #{report.equipment_id}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <User className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Craftsman</p>
                  <p className="text-sm font-medium text-gray-900">Craftsman #{report.craftsman_id}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <FileText className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Work Order</p>
                  <p className="text-sm font-medium text-gray-900">WO-{report.work_order_id}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Clock className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Labor Hours</p>
                  <p className="text-sm font-medium text-gray-900">
                    {report.labor_hours ? `${report.labor_hours}h` : 'Not specified'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Dates */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Dates</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Completed At</p>
                <p className="text-sm font-medium text-gray-900">{formatDate(report.completed_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Created At</p>
                <p className="text-sm font-medium text-gray-900">{formatDate(report.created_at)}</p>
              </div>
              {report.reviewed_at && (
                <div>
                  <p className="text-sm text-gray-500">Reviewed At</p>
                  <p className="text-sm font-medium text-gray-900">{formatDate(report.reviewed_at)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Status</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Equipment Operational</span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    report.equipment_operational
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {report.equipment_operational ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Follow-up Required</span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    report.follow_up_required
                      ? 'bg-orange-100 text-orange-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {report.follow_up_required ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Reviewed</span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    report.reviewed_by
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {report.reviewed_by ? 'Yes' : 'Pending'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Work Performed */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Work Performed</h2>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{report.work_performed}</p>
          </div>

          {/* Findings */}
          {report.findings && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Findings</h2>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{report.findings}</p>
            </div>
          )}

          {/* Recommendations */}
          {report.recommendations && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Recommendations</h2>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{report.recommendations}</p>
            </div>
          )}

          {/* Parts Used */}
          {report.parts_used && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Parts Used</h2>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{report.parts_used}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MaintenanceDetailPage
