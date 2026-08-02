import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Download, RefreshCw } from 'lucide-react'
import EquipmentTable from '../../components/equipment/EquipmentTable'
import EquipmentFilters from '../../components/equipment/EquipmentFilters'
import type { Equipment } from '../../types'
import { equipmentService, type EquipmentFilters as Filters } from '../../services/equipment.service'

const EquipmentListPage: React.FC = () => {
  const navigate = useNavigate()
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState<Filters>({
    page: 1,
    limit: 20,
  })
  const [stats, setStats] = useState({
    total: 0,
    operational: 0,
    maintenance: 0,
    breakdown: 0,
    retired: 0,
  })

  // Load equipment
  const loadEquipment = async () => {
    try {
      setIsLoading(true)
      const response = await equipmentService.getAll(filters)
      setEquipment(response.data)
    } catch (error) {
      console.error('Failed to load equipment:', error)
      // Silently fail - user can see loading state or empty table
    } finally {
      setIsLoading(false)
    }
  }

  // Load statistics
  const loadStatistics = async () => {
    try {
      const statistics = await equipmentService.getStatistics()
      setStats(statistics)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  useEffect(() => {
    loadEquipment()
    loadStatistics()
  }, [filters])

  // Handle delete
  const handleDelete = async (equipment: Equipment) => {
    if (!confirm(`Are you sure you want to delete ${equipment.name}?`)) {
      return
    }

    try {
      await equipmentService.delete(equipment.id)
      loadEquipment()
      loadStatistics()
    } catch (error) {
      console.error('Failed to delete equipment:', error)
      // Silently fail
    }
  }

  // Handle view
  const handleView = (equipment: Equipment) => {
    navigate(`/equipment/${equipment.id}`)
  }

  // Handle edit
  const handleEdit = (equipment: Equipment) => {
    navigate(`/equipment/${equipment.id}/edit`)
  }

  // Handle export
  const handleExport = async () => {
    try {
      await equipmentService.exportToCSV(filters)
    } catch (error) {
      console.error('Failed to export equipment:', error)
      // Silently fail
    }
  }

  // Handle clear filters
  const handleClearFilters = () => {
    setFilters({
      page: 1,
      limit: 20,
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Equipment Management</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage and track all production equipment
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => loadEquipment()}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <button
              onClick={() => navigate('/equipment/new')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              Add Equipment
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm font-medium text-gray-600">Total Equipment</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm font-medium text-gray-600">Operational</div>
            <div className="text-2xl font-bold text-green-600 mt-1">{stats.operational}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm font-medium text-gray-600">Maintenance</div>
            <div className="text-2xl font-bold text-yellow-600 mt-1">{stats.maintenance}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm font-medium text-gray-600">Breakdown</div>
            <div className="text-2xl font-bold text-red-600 mt-1">{stats.breakdown}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm font-medium text-gray-600">Retired</div>
            <div className="text-2xl font-bold text-gray-600 mt-1">{stats.retired}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6">
        <EquipmentFilters
          filters={filters}
          onFiltersChange={setFilters}
          onClear={handleClearFilters}
        />
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading equipment...</p>
        </div>
      ) : (
        <EquipmentTable
          equipment={equipment}
          onView={handleView}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
    </div>
  )
}

export default EquipmentListPage
