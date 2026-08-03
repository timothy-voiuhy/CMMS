import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ClipboardCheck,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
} from 'lucide-react'
import {
  qualityService,
  type QualityInspection,
  type NonConformanceReport,
  type QualityStatistics,
} from '../../services/quality.service'

type TabType = 'inspections' | 'ncrs'

const QualityPage: React.FC = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<TabType>('inspections')
  const [statistics, setStatistics] = useState<QualityStatistics | null>(null)
  const [inspections, setInspections] = useState<QualityInspection[]>([])
  const [ncrs, setNCRs] = useState<NonConformanceReport[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    loadData()
  }, [activeTab, searchTerm, statusFilter])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const stats = await qualityService.getStatistics()
      setStatistics(stats)

      if (activeTab === 'inspections') {
        const response = await qualityService.getInspections({
          limit: 50,
          search: searchTerm || undefined,
          status: statusFilter || undefined,
        })
        setInspections(response.data)
      } else {
        const response = await qualityService.getNCRs({
          limit: 50,
          search: searchTerm || undefined,
          status: statusFilter || undefined,
        })
        setNCRs(response.data)
      }
    } catch (error) {
      console.error('Failed to load quality data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteInspection = async (id: number) => {
    if (!confirm('Are you sure you want to delete this inspection?')) return
    try {
      await qualityService.deleteInspection(id)
      loadData()
    } catch (error) {
      console.error('Failed to delete inspection:', error)
      alert('Failed to delete inspection')
    }
  }

  const handleDeleteNCR = async (id: number) => {
    if (!confirm('Are you sure you want to delete this NCR?')) return
    try {
      await qualityService.deleteNCR(id)
      loadData()
    } catch (error) {
      console.error('Failed to delete NCR:', error)
      alert('Failed to delete NCR')
    }
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { bg: string; text: string; icon: any }> = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock },
      in_progress: { bg: 'bg-blue-100', text: 'text-blue-800', icon: Clock },
      completed: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
      failed: { bg: 'bg-red-100', text: 'text-red-800', icon: XCircle },
      open: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock },
      investigating: { bg: 'bg-blue-100', text: 'text-blue-800', icon: Search },
      corrective_action: { bg: 'bg-purple-100', text: 'text-purple-800', icon: Edit },
      closed: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
      rejected: { bg: 'bg-gray-100', text: 'text-gray-800', icon: XCircle },
    }

    const config = statusMap[status] || statusMap.pending
    const Icon = config.icon

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${config.bg} ${config.text}`}>
        <Icon className="w-3 h-3" />
        {status.replace('_', ' ')}
      </span>
    )
  }

  const getResultBadge = (result: string) => {
    const resultMap: Record<string, { bg: string; text: string }> = {
      pass: { bg: 'bg-green-100', text: 'text-green-800' },
      fail: { bg: 'bg-red-100', text: 'text-red-800' },
      conditional: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
      pending: { bg: 'bg-gray-100', text: 'text-gray-800' },
    }

    const config = resultMap[result] || resultMap.pending

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${config.bg} ${config.text}`}>
        {result}
      </span>
    )
  }

  const getSeverityBadge = (severity: string) => {
    const severityMap: Record<string, { bg: string; text: string }> = {
      critical: { bg: 'bg-red-100', text: 'text-red-800' },
      major: { bg: 'bg-orange-100', text: 'text-orange-800' },
      minor: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
    }

    const config = severityMap[severity] || severityMap.minor

    return (
      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${config.bg} ${config.text}`}>
        {severity}
      </span>
    )
  }

  if (isLoading && !statistics) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Quality Control</h1>
        <p className="text-gray-600 mt-1">Manage inspections and non-conformance reports</p>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Inspections</p>
                <p className="text-2xl font-bold text-gray-800">{statistics.total_inspections}</p>
                <p className="text-xs text-gray-500 mt-1">{statistics.pending_inspections} pending</p>
              </div>
              <ClipboardCheck className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pass Rate</p>
                <p className="text-2xl font-bold text-green-600">{statistics.pass_rate.toFixed(1)}%</p>
                <p className="text-xs text-gray-500 mt-1">{statistics.fail_rate.toFixed(1)}% fail rate</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total NCRs</p>
                <p className="text-2xl font-bold text-orange-600">{statistics.total_ncrs}</p>
                <p className="text-xs text-gray-500 mt-1">{statistics.open_ncrs} open</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-orange-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Critical NCRs</p>
                <p className="text-2xl font-bold text-red-600">{statistics.critical_ncrs}</p>
                <p className="text-xs text-gray-500 mt-1">Avg {statistics.avg_defects_per_inspection.toFixed(1)} defects</p>
              </div>
              <XCircle className="w-8 h-8 text-red-500" />
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <div className="flex items-center justify-between px-6 pt-4">
            <div className="flex space-x-4">
              <button
                onClick={() => setActiveTab('inspections')}
                className={`pb-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'inspections'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Quality Inspections
              </button>
              <button
                onClick={() => setActiveTab('ncrs')}
                className={`pb-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'ncrs'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Non-Conformance Reports
              </button>
            </div>
            <button
              onClick={() => navigate(activeTab === 'inspections' ? '/quality/inspections/new' : '/quality/ncrs/new')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              {activeTab === 'inspections' ? 'New Inspection' : 'New NCR'}
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              {activeTab === 'inspections' ? (
                <>
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </>
              ) : (
                <>
                  <option value="open">Open</option>
                  <option value="investigating">Investigating</option>
                  <option value="corrective_action">Corrective Action</option>
                  <option value="closed">Closed</option>
                  <option value="rejected">Rejected</option>
                </>
              )}
            </select>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'inspections' ? (
            inspections.length === 0 ? (
              <div className="text-center py-12">
                <ClipboardCheck className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No inspections found</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Inspection #</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Result</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pass Rate</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {inspections.map((inspection) => (
                      <tr key={inspection.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {inspection.inspection_number}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{inspection.product_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{inspection.inspection_type}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {new Date(inspection.inspection_date).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(inspection.status)}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{getResultBadge(inspection.result)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {inspection.pass_rate ? `${inspection.pass_rate.toFixed(1)}%` : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => navigate(`/quality/inspections/${inspection.id}`)}
                              className="text-blue-600 hover:text-blue-900"
                              title="View"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => navigate(`/quality/inspections/${inspection.id}/edit`)}
                              className="text-green-600 hover:text-green-900"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteInspection(inspection.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          ) : (
            ncrs.length === 0 ? (
              <div className="text-center py-12">
                <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No NCRs found</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">NCR #</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {ncrs.map((ncr) => (
                      <tr key={ncr.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {ncr.ncr_number}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{ncr.title}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{getSeverityBadge(ncr.severity)}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(ncr.status)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {new Date(ncr.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {ncr.estimated_cost ? `$${ncr.estimated_cost.toLocaleString()}` : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => navigate(`/quality/ncrs/${ncr.id}`)}
                              className="text-blue-600 hover:text-blue-900"
                              title="View"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => navigate(`/quality/ncrs/${ncr.id}/edit`)}
                              className="text-green-600 hover:text-green-900"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteNCR(ncr.id)}
                              className="text-red-600 hover:text-red-900"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  )
}

export default QualityPage
