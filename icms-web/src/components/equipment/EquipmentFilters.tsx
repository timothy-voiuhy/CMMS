import React from 'react'
import { Search, Filter, X } from 'lucide-react'
import type { EquipmentFilters as Filters } from '../../services/equipment.service'

interface EquipmentFiltersProps {
  filters: Filters
  onFiltersChange: (filters: Filters) => void
  onClear: () => void
}

const EquipmentFilters: React.FC<EquipmentFiltersProps> = ({
  filters,
  onFiltersChange,
  onClear,
}) => {
  const hasActiveFilters = filters.category || filters.status || filters.location || filters.search

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Filters</h3>
        </div>
        {hasActiveFilters && (
          <button
            onClick={onClear}
            className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
          >
            <X className="w-4 h-4" />
            Clear filters
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
          <input
            type="text"
            placeholder="Search equipment..."
            value={filters.search || ''}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
          />
        </div>

        {/* Category Filter */}
        <select
          value={filters.category || ''}
          onChange={(e) => onFiltersChange({ ...filters, category: e.target.value || undefined })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
        >
          <option value="">All Categories</option>
          <option value="Potato Crisps Line">Potato Crisps Line</option>
          <option value="Fried Corn Line">Fried Corn Line</option>
          <option value="Utilities">Utilities</option>
          <option value="Conveyors">Conveyors</option>
        </select>

        {/* Status Filter */}
        <select
          value={filters.status || ''}
          onChange={(e) => onFiltersChange({ ...filters, status: e.target.value || undefined })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
        >
          <option value="">All Statuses</option>
          <option value="OPERATIONAL">Operational</option>
          <option value="MAINTENANCE">Maintenance</option>
          <option value="BREAKDOWN">Breakdown</option>
          <option value="RETIRED">Retired</option>
        </select>

        {/* Location Filter */}
        <select
          value={filters.location || ''}
          onChange={(e) => onFiltersChange({ ...filters, location: e.target.value || undefined })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
        >
          <option value="">All Locations</option>
          <option value="Production Line 1">Production Line 1</option>
          <option value="Production Line 2">Production Line 2</option>
          <option value="Generator House">Generator House</option>
          <option value="Tank Farm">Tank Farm</option>
          <option value="Well 1">Well 1</option>
          <option value="Well 2">Well 2</option>
          <option value="Well 3">Well 3</option>
        </select>
      </div>
    </div>
  )
}

export default EquipmentFilters
