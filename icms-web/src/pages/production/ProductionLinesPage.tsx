import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus,
  Factory,
  Activity,
  Pause,
  Wrench as WrenchIcon,
  Search,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
} from 'lucide-react'
import {
  productionLineService,
  type ProductionLine,
  type ProductionLineStatistics,
  type ProductionLineStatus,
} from '../../services/production.service'

const ProductionLinesPage: React.FC = () => {
  const navigate = useNavigate()
  const [lines, setLines] = useState<ProductionLine[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [statistics, setStatistics] = useState<ProductionLineStatistics | null>(null)
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    search: '',
    status: '' as ProductionLineStatus | '',
  })
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    loadLines()
    loadStatistics()
  }, [filters])

  const loadLines = async () => {
    try {
      setIsLoading(true)
      const response = await productionLineService.getAll(filters)
      setLines(response.data)
      setTotalPages(response.totalPages)
    } catch (error) {
      console.error('Failed to load production lines:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const stats = await productionLineService.getStatistics()
      setStatistics(stats)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const handleDelete = async (line: ProductionLine) => {
    if (!confirm(`Are you sure you want to delete production line ${line.name}?`)) return

    try {
      await productionLineService.delete(line.id)
      loadLines()
      loadStatistics()
    } catch (error) {
      console.error('Failed to delete production line:', error)
      alert('Failed to delete production line')
    }
  }

  const getStatusBadge = (status: ProductionLineStatus) => {
    const badges = {
      active: { bg: 'bg-green-100', text: 'text-green-800', icon: Activity },
      idle: { bg: 'bg-gray-100', text: 'text-gray-800', icon: Pause },
      maintenance: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: WrenchIcon },
      offline: { bg: 'bg-red-100', text: 'text-red-800', icon: Pause },
    }
    return badges[status] || badges.idle
  }

  const formatStatus = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Production Lines</h1>
            <p className="text-gray-600 mt-1">Manage and monitor production lines</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                loadLines()
                loadStatistics()
              }}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={() => navigate('/production/lines/new')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              New Production Line
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Lines</p>
                  <p className="text-2xl font-bold text-gray-800">{statistics.total}</p>
                </div>
                <Factory className="w-8 h-8 text-blue-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.active}</p>
                </div>
                <Activity className="w-8 h-8 text-green-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Idle</p>
                  <p className="text-2xl font-bold text-gray-600">{statistics.idle}</p>
                </div>
                <Pause className="w-8 h-8 text-gray-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Maintenance</p>
                  <p className="text-2xl font-bold text-yellow-600">{statistics.maintenance}</p>
                </div>
                <WrenchIcon className="w-8 h-8 text-yellow-500" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
                placeholder="Search by line code or name..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filters.status}
              onChange={(e) =>
                setFilters({ ...filters, status: e.target.value as ProductionLineStatus | '', page: 1 })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="idle">Idle</option>
              <option value="maintenance">Maintenance</option>
              <option value="offline">Offline</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading production lines...</p>
          </div>
        ) : lines.length === 0 ? (
          <div className="p-8 text-center">
            <Factory className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No production lines found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Line Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Capacity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {lines.map((line) => {
                    const statusBadge = getStatusBadge(line.status)
                    const StatusIcon = statusBadge.icon
                    return (
                      <tr 
                        key={line.id} 
                        onClick={() => navigate(`/production/lines/${line.id}`)}
                        className="hover:bg-blue-50 cursor-pointer transition-colors"
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{line.line_code}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{line.name}</div>
                          {line.description && (
                            <div className="text-sm text-gray-500 truncate max-w-xs">
                              {line.description}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{line.location || '-'}</div>
                          {line.floor && <div className="text-sm text-gray-500">Floor: {line.floor}</div>}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {line.capacity_per_hour
                              ? `${line.capacity_per_hour} ${line.capacity_unit || 'units'}/hr`
                              : '-'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full ${statusBadge.bg} ${statusBadge.text} flex items-center gap-1 w-fit`}
                          >
                            <StatusIcon className="w-3 h-3" />
                            {formatStatus(line.status)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                            <button
                              onClick={() => navigate(`/production/lines/${line.id}`)}
                              className="text-blue-600 hover:text-blue-900"
                              title="View Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => navigate(`/production/lines/${line.id}/edit`)}
                              className="text-green-600 hover:text-green-900"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(line)}
                              className="text-red-600 hover:text-red-900"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
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

export default ProductionLinesPage
