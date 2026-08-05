import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Download, RefreshCw } from 'lucide-react'
import EquipmentTable from '../../components/equipment/EquipmentTable'
import EquipmentFilters from '../../components/equipment/EquipmentFilters'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import type { Equipment } from '../../types'
import { equipmentService, type EquipmentFilters as Filters } from '../../services/equipment.service'

const EquipmentListPage: React.FC = () => {
  const navigate = useNavigate()
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [deleteDialog, setDeleteDialog] = useState<{ isOpen: boolean; equipment: Equipment | null }>({
    isOpen: false,
    equipment: null,
  })
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  })
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
      setPagination({
        total: response.total,
        page: response.page,
        pageSize: response.pageSize,
        totalPages: response.totalPages
      })
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
  const handleDelete = (equipment: Equipment) => {
    setDeleteDialog({ isOpen: true, equipment })
  }

  const confirmDelete = async () => {
    if (!deleteDialog.equipment) return

    try {
      await equipmentService.delete(deleteDialog.equipment.id)
      loadEquipment()
      loadStatistics()
    } catch (error) {
      console.error('Failed to delete equipment:', error)
      alert('Failed to delete equipment. It may be in use.')
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between mb-2">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Equipment Management</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Manage and track all production equipment
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center sm:gap-3">
            <button
              onClick={() => loadEquipment()}
              className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={handleExport}
              className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <button
              onClick={() => navigate('/equipment/new')}
              className="col-span-2 flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 sm:col-span-1"
            >
              <Plus className="w-4 h-4" />
              Add Equipment
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 sm:gap-4 mt-4">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Equipment</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">{stats.total}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Operational</div>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{stats.operational}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Maintenance</div>
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">{stats.maintenance}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Breakdown</div>
            <div className="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{stats.breakdown}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Retired</div>
            <div className="text-2xl font-bold text-gray-600 dark:text-gray-400 mt-1">{stats.retired}</div>
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
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading equipment...</p>
        </div>
      ) : (
        <>
          <EquipmentTable
            equipment={equipment}
            onView={handleView}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
          
          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between bg-white dark:bg-gray-800 px-4 sm:px-6 py-3 rounded-lg shadow border border-gray-200 dark:border-gray-700">
              <div className="text-sm text-gray-700 dark:text-gray-300">
                Showing <span className="font-medium">{((pagination.page - 1) * pagination.pageSize) + 1}</span> to{' '}
                <span className="font-medium">{Math.min(pagination.page * pagination.pageSize, pagination.total)}</span> of{' '}
                <span className="font-medium">{pagination.total}</span> results
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page! - 1 })}
                  disabled={pagination.page === 1}
                  className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300"
                >
                  Previous
                </button>
                
                {/* Page numbers */}
                {Array.from({ length: pagination.totalPages }, (_, i) => i + 1).map((pageNum) => (
                  <button
                    key={pageNum}
                    onClick={() => setFilters({ ...filters, page: pageNum })}
                    className={`px-3 py-1 text-sm border rounded ${
                      pageNum === pagination.page
                        ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-600 dark:border-blue-500'
                        : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    {pageNum}
                  </button>
                ))}
                
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page! + 1 })}
                  disabled={pagination.page === pagination.totalPages}
                  className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteDialog.isOpen}
        onClose={() => setDeleteDialog({ isOpen: false, equipment: null })}
        onConfirm={confirmDelete}
        title="Delete Equipment"
        message="Are you sure you want to delete this equipment? This action cannot be undone."
        confirmText="Delete Equipment"
        cancelText="Cancel"
        type="danger"
        itemName={deleteDialog.equipment ? `${deleteDialog.equipment.name} (${deleteDialog.equipment.equipment_id})` : ''}
      />
    </div>
  )
}

export default EquipmentListPage
