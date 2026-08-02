import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Download, RefreshCw, Users } from 'lucide-react'
import type { CraftsmanWithUser } from '../../services/craftsman.service'
import { craftsmanService, type CraftsmanFilters } from '../../services/craftsman.service'

const CraftsmenListPage: React.FC = () => {
  const navigate = useNavigate()
  const [craftsmen, setCraftsmen] = useState<CraftsmanWithUser[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState<CraftsmanFilters>({
    page: 1,
    limit: 20,
  })
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    inactive: 0,
    byDepartment: {} as Record<string, number>,
  })
  const [searchTerm, setSearchTerm] = useState('')

  // Load craftsmen
  const loadCraftsmen = async () => {
    try {
      setIsLoading(true)
      const response = await craftsmanService.getAll(filters)
      setCraftsmen(response.data)
    } catch (error) {
      console.error('Failed to load craftsmen:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Load statistics
  const loadStatistics = async () => {
    try {
      const statistics = await craftsmanService.getOverallStatistics()
      setStats(statistics)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  useEffect(() => {
    loadCraftsmen()
    loadStatistics()
  }, [filters])

  const handleSearch = () => {
    setFilters({ ...filters, search: searchTerm, page: 1 })
  }

  const handleView = (craftsman: CraftsmanWithUser) => {
    navigate(`/craftsmen/${craftsman.id}`)
  }

  const handleRefresh = () => {
    loadCraftsmen()
    loadStatistics()
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Craftsmen Management</h1>
            <p className="text-gray-600 mt-1">Manage your workforce and their skills</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleRefresh}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={() => navigate('/craftsmen/new')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Craftsman
            </button>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Craftsmen</p>
              <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active</p>
              <p className="text-2xl font-bold text-green-600">{stats.active}</p>
            </div>
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 font-bold">✓</span>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Inactive</p>
              <p className="text-2xl font-bold text-gray-600">{stats.inactive}</p>
            </div>
            <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
              <span className="text-gray-600 font-bold">−</span>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Departments</p>
              <p className="text-2xl font-bold text-blue-600">
                {Object.keys(stats.byDepartment).length}
              </p>
            </div>
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-bold">#</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by name, employee ID, or department..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={handleSearch}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Search
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Employee ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Department
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Position
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
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
                {craftsmen.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      <Users className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                      <p className="text-sm">No craftsmen found</p>
                    </td>
                  </tr>
                ) : (
                  craftsmen.map((craftsman) => (
                    <tr
                      key={craftsman.id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleView(craftsman)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          {craftsman.employee_id}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                            <span className="text-blue-600 font-semibold text-sm">
                              {craftsman.full_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {craftsman.full_name}
                            </div>
                            <div className="text-sm text-gray-500">{craftsman.username}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {craftsman.department || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {craftsman.position || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{craftsman.email}</div>
                        {craftsman.phone && (
                          <div className="text-sm text-gray-500">{craftsman.phone}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            craftsman.user?.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {craftsman.user?.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleView(craftsman)
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default CraftsmenListPage
