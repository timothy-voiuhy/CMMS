import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus,
  Package,
  AlertTriangle,
  DollarSign,
  Search,
  Filter,
  RefreshCw,
  Edit,
  Trash2,
  Eye,
  TrendingDown,
  Grid,
} from 'lucide-react'
import {
  inventoryService,
  type InventoryItem,
  type InventoryCategory,
  type InventoryStatistics,
} from '../../services/inventory.service'

const InventoryListPage: React.FC = () => {
  const navigate = useNavigate()
  const [items, setItems] = useState<InventoryItem[]>([])
  const [categories, setCategories] = useState<InventoryCategory[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [statistics, setStatistics] = useState<InventoryStatistics | null>(null)
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    search: '',
    category_id: undefined as number | undefined,
    low_stock: false,
  })
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    loadItems()
    loadStatistics()
  }, [filters])

  const loadCategories = async () => {
    try {
      const cats = await inventoryService.getCategories()
      setCategories(cats)
    } catch (error) {
      console.error('Failed to load categories:', error)
    }
  }

  const loadItems = async () => {
    try {
      setIsLoading(true)
      const response = await inventoryService.getAll(filters)
      setItems(response.data)
      setTotalPages(response.totalPages)
    } catch (error) {
      console.error('Failed to load inventory items:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const stats = await inventoryService.getStatistics()
      setStatistics(stats)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const handleDelete = async (item: InventoryItem) => {
    if (!confirm(`Are you sure you want to delete ${item.name}?`)) return

    try {
      await inventoryService.delete(item.id)
      loadItems()
      loadStatistics()
    } catch (error) {
      console.error('Failed to delete item:', error)
      alert('Failed to delete item')
    }
  }

  const getStockStatus = (item: InventoryItem) => {
    if (item.quantity <= 0) return 'out-of-stock'
    if (item.reorder_point && item.quantity <= item.reorder_point) return 'low-stock'
    return 'in-stock'
  }

  const getStockBadge = (item: InventoryItem) => {
    const status = getStockStatus(item)
    if (status === 'out-of-stock') {
      return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Out of Stock</span>
    }
    if (status === 'low-stock') {
      return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">Low Stock</span>
    }
    return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">In Stock</span>
  }

  const formatCategory = (category: string) => {
    return category.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Inventory Management</h1>
            <p className="text-gray-600 mt-1">Track and manage inventory items</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/inventory/grid')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Grid className="w-4 h-4" />
              Grid View
            </button>
            <button
              onClick={() => navigate('/inventory/categories')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Filter className="w-4 h-4" />
              Manage Categories
            </button>
            <button
              onClick={() => {
                loadItems()
                loadStatistics()
              }}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={() => navigate('/inventory/new')}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              Add Item
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Items</p>
                  <p className="text-2xl font-bold text-gray-800">{statistics.total_items}</p>
                </div>
                <Package className="w-8 h-8 text-blue-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Low Stock</p>
                  <p className="text-2xl font-bold text-yellow-600">{statistics.low_stock_count}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-yellow-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Out of Stock</p>
                  <p className="text-2xl font-bold text-red-600">{statistics.out_of_stock_count}</p>
                </div>
                <TrendingDown className="w-8 h-8 text-red-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Value</p>
                  <p className="text-2xl font-bold text-green-600">${statistics.total_value.toLocaleString()}</p>
                </div>
                <DollarSign className="w-8 h-8 text-green-500" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
                placeholder="Search by name, code, or description..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={filters.category_id || ''}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  category_id: e.target.value ? parseInt(e.target.value) : undefined,
                  page: 1,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Stock Status</label>
            <label className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="checkbox"
                checked={filters.low_stock}
                onChange={(e) => setFilters({ ...filters, low_stock: e.target.checked, page: 1 })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm">Low Stock Only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading inventory...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center">
            <Package className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No inventory items found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Item Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Unit Cost
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {items.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{item.item_code}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{item.name}</div>
                        {item.description && (
                          <div className="text-sm text-gray-500">{item.description}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{item.category?.name || 'Uncategorized'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {item.quantity} {item.unit_of_measure}
                        </div>
                        {item.reorder_point && (
                          <div className="text-xs text-gray-500">
                            Reorder: {item.reorder_point}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {item.unit_cost ? `$${item.unit_cost.toFixed(2)}` : '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">{getStockBadge(item)}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{item.location || '-'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => navigate(`/inventory/${item.id}`)}
                            className="text-blue-600 hover:text-blue-900"
                            title="View Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => navigate(`/inventory/${item.id}/edit`)}
                            className="text-green-600 hover:text-green-900"
                            title="Edit"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(item)}
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

export default InventoryListPage
