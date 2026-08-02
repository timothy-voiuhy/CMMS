import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus,
  FileText,
  Clock,
  CheckCircle,
  AlertTriangle,
  Search,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
} from 'lucide-react'
import {
  maintenanceService,
  type MaintenanceReport,
  type MaintenanceStatistics,
} from '../../services/maintenance.service'

const MaintenanceListPage: React.FC = () => {
  const navigate = useNavigate()
  const [reports, setReports] = useState<MaintenanceReport[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [statistics, setStatistics] = useState<MaintenanceStatistics | null>(null)
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    search: '',
  })
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    loadReports()
    loadStatistics()
  }, [filters])

  const loadReports = async () => {
    try {
      setIsLoading(true)
      const response = await maintenanceService.getAll(filters)
      setReports(response.data)
      setTotalPages(response.totalPages)
    } catch (error) {
      console.error('Failed to load maintenance reports:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const stats = await maintenanceService.getStatistics()
      setStatistics(stats)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const handleDelete = async (report: MaintenanceReport) => {
    if (!confirm(`Are you sure you want to delete report ${report.report_number}?`)) return

    try {
      await maintenanceService.delete(report.id)
      loadReports()
      loadStatistics()
    } catch (error) {
      console.error('Failed to delete report:', error)
      alert('Failed to delete report')
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Maintenance Reports</h1>
            <p className="text-gray-600 mt-1">Track and manage maintenance activities</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                loadReports()
                loadStatistics()
              }}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={() => navigate('/maintenance/new')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              New Report
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Reports</p>
                  <p className="text-2xl font-bold text-gray-800">{statistics.total_reports}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Reviewed</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.reviewed_count}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Pending Review</p>
                  <p className="text-2xl font-bold text-yellow-600">{statistics.pending_review}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Follow-up Required</p>
                  <p className="text-2xl font-bold text-orange-600">{statistics.follow_up_required}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-orange-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Labor Hours</p>
                  <p className="text-2xl font-bold text-purple-600">{statistics.total_labor_hours.toFixed(1)}</p>
                </div>
                <Clock className="w-8 h-8 text-purple-500" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
            placeholder="Search by report number, work performed, or findings..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading maintenance reports...</p>
          </div>
        ) : reports.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No maintenance reports found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Report #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Equipment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Craftsman
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Work Performed
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Labor Hours
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {reports.map((report) => (
                    <tr key={report.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{report.report_number}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">Equipment #{report.equipment_id}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">Craftsman #{report.craftsman_id}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-xs truncate">
                          {report.work_performed}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {report.labor_hours ? `${report.labor_hours}h` : '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col gap-1">
                          {report.reviewed_by ? (
                            <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                              Reviewed
                            </span>
                          ) : (
                            <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                              Pending Review
                            </span>
                          )}
                          {report.follow_up_required && (
                            <span className="px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 rounded-full">
                              Follow-up
                            </span>
                          )}
                          {!report.equipment_operational && (
                            <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                              Not Operational
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(report.completed_at)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => navigate(`/maintenance/${report.id}`)}
                            className="text-blue-600 hover:text-blue-900"
                            title="View Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => navigate(`/maintenance/${report.id}/edit`)}
                            className="text-green-600 hover:text-green-900"
                            title="Edit"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(report)}
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

            {/* Pagination */}
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Page {filters.page} of {totalPages}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                  disabled={filters.page === 1}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                  disabled={filters.page === totalPages}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default MaintenanceListPage
