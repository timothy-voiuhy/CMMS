import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Box, Hammer, ImageIcon, Plus, RefreshCw, Save, Search, Trash2, Wrench, X } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import {
  maintenanceService,
  type CreateMaintenanceCatalogueItemRequest,
  type MaintenanceCatalogueItem,
  type MaintenanceCatalogueItemType,
} from '../../services/maintenance.service'

const emptyItem = (): CreateMaintenanceCatalogueItemRequest => ({
  item_code: '',
  item_type: 'spare_part',
  name: '',
  description: '',
  category: '',
  image_url: '',
  manufacturer: '',
  model_number: '',
  supplier: '',
  unit_of_measure: '',
  unit_cost: undefined,
  location: '',
  compatible_equipment: '',
  inventory_item_id: undefined,
  is_active: true,
  notes: '',
})

const getErrorMessage = (error: unknown, fallback: string) => {
  const response = (error as { response?: { data?: { detail?: unknown } } }).response
  return typeof response?.data?.detail === 'string' ? response.data.detail : fallback
}

const formatType = (type: MaintenanceCatalogueItemType) => type === 'tool' ? 'Tool' : 'Spare Part'

const MaintenanceCataloguePage: React.FC = () => {
  const { hasPermission } = useAuthStore()
  const [items, setItems] = useState<MaintenanceCatalogueItem[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState<MaintenanceCatalogueItem | null>(null)
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    search: '',
    category: '',
    item_type: '' as MaintenanceCatalogueItemType | '',
    include_inactive: false,
  })
  const [formData, setFormData] = useState<CreateMaintenanceCatalogueItemRequest>(emptyItem())

  const canCreate = hasPermission('maintenance.catalogue.create')
  const canEdit = hasPermission('maintenance.catalogue.edit')
  const canDelete = hasPermission('maintenance.catalogue.delete')

  const loadCatalogue = useCallback(async () => {
    try {
      setIsLoading(true)
      const [catalogueResponse, categoriesResponse] = await Promise.all([
        maintenanceService.getCatalogue({
          page: filters.page,
          limit: filters.limit,
          search: filters.search || undefined,
          category: filters.category || undefined,
          item_type: filters.item_type || undefined,
          include_inactive: filters.include_inactive,
        }),
        maintenanceService.getCatalogueCategories(),
      ])
      setItems(catalogueResponse.data)
      setTotalPages(catalogueResponse.totalPages)
      setCategories(categoriesResponse)
    } catch (error) {
      console.error('Failed to load maintenance catalogue:', error)
    } finally {
      setIsLoading(false)
    }
  }, [filters])

  useEffect(() => {
    void Promise.resolve().then(loadCatalogue)
  }, [loadCatalogue])

  const stats = useMemo(() => ({
    spareParts: items.filter((item) => item.item_type === 'spare_part').length,
    tools: items.filter((item) => item.item_type === 'tool').length,
    inactive: items.filter((item) => !item.is_active).length,
  }), [items])

  const startCreate = () => {
    setEditingItem(null)
    setFormData(emptyItem())
    setShowForm(true)
  }

  const startEdit = (item: MaintenanceCatalogueItem) => {
    setEditingItem(item)
    setFormData({
      item_code: item.item_code,
      item_type: item.item_type,
      name: item.name,
      description: item.description || '',
      category: item.category || '',
      image_url: item.image_url || '',
      manufacturer: item.manufacturer || '',
      model_number: item.model_number || '',
      supplier: item.supplier || '',
      unit_of_measure: item.unit_of_measure || '',
      unit_cost: item.unit_cost,
      location: item.location || '',
      compatible_equipment: item.compatible_equipment || '',
      inventory_item_id: item.inventory_item_id,
      is_active: item.is_active,
      notes: item.notes || '',
    })
    setShowForm(true)
  }

  const buildPayload = (): CreateMaintenanceCatalogueItemRequest => ({
    ...formData,
    item_code: formData.item_code || undefined,
    description: formData.description || undefined,
    category: formData.category || undefined,
    image_url: formData.image_url || undefined,
    manufacturer: formData.manufacturer || undefined,
    model_number: formData.model_number || undefined,
    supplier: formData.supplier || undefined,
    unit_of_measure: formData.unit_of_measure || undefined,
    unit_cost: formData.unit_cost ?? undefined,
    location: formData.location || undefined,
    compatible_equipment: formData.compatible_equipment || undefined,
    inventory_item_id: formData.inventory_item_id || undefined,
    notes: formData.notes || undefined,
  })

  const handleSave = async () => {
    if (!formData.name.trim()) {
      alert('Name is required')
      return
    }

    try {
      setIsSaving(true)
      if (editingItem) {
        await maintenanceService.updateCatalogueItem(editingItem.id, buildPayload())
      } else {
        await maintenanceService.createCatalogueItem(buildPayload())
      }
      setShowForm(false)
      await loadCatalogue()
    } catch (error: unknown) {
      console.error('Failed to save catalogue item:', error)
      alert(getErrorMessage(error, 'Failed to save catalogue item'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async (item: MaintenanceCatalogueItem) => {
    if (!confirm(`Deactivate ${item.name}?`)) return

    try {
      await maintenanceService.deleteCatalogueItem(item.id)
      await loadCatalogue()
    } catch (error: unknown) {
      console.error('Failed to deactivate catalogue item:', error)
      alert(getErrorMessage(error, 'Failed to deactivate catalogue item'))
    }
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Parts & Tools Catalogue</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Maintain reference details for spare parts, tools, images, suppliers, and equipment compatibility</p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center sm:gap-3">
            <button
              onClick={loadCatalogue}
              className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            {canCreate && (
              <button
                onClick={startCreate}
                className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
              >
                <Plus className="w-4 h-4" />
                New Item
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Spare Parts</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.spareParts}</p>
              </div>
              <Box className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Tools</p>
                <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{stats.tools}</p>
              </div>
              <Hammer className="w-8 h-8 text-emerald-500" />
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Inactive</p>
                <p className="text-2xl font-bold text-gray-700 dark:text-gray-200">{stats.inactive}</p>
              </div>
              <Wrench className="w-8 h-8 text-gray-500" />
            </div>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{editingItem ? 'Edit Catalogue Item' : 'New Catalogue Item'}</h2>
            <button onClick={() => setShowForm(false)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name</label>
              <input value={formData.name} onChange={(event) => setFormData({ ...formData, name: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Code</label>
              <input value={formData.item_code || ''} onChange={(event) => setFormData({ ...formData, item_code: event.target.value })} placeholder="Auto-generated if empty" className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Type</label>
              <select value={formData.item_type} onChange={(event) => setFormData({ ...formData, item_type: event.target.value as MaintenanceCatalogueItemType })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="spare_part">Spare Part</option>
                <option value="tool">Tool</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category</label>
              <input value={formData.category || ''} onChange={(event) => setFormData({ ...formData, category: event.target.value })} placeholder="Bearings, Belts, Hand Tools..." className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Image URL</label>
              <input value={formData.image_url || ''} onChange={(event) => setFormData({ ...formData, image_url: event.target.value })} placeholder="https://..." className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Manufacturer</label>
              <input value={formData.manufacturer || ''} onChange={(event) => setFormData({ ...formData, manufacturer: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Model Number</label>
              <input value={formData.model_number || ''} onChange={(event) => setFormData({ ...formData, model_number: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Supplier</label>
              <input value={formData.supplier || ''} onChange={(event) => setFormData({ ...formData, supplier: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Location</label>
              <input value={formData.location || ''} onChange={(event) => setFormData({ ...formData, location: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Unit</label>
              <input value={formData.unit_of_measure || ''} onChange={(event) => setFormData({ ...formData, unit_of_measure: event.target.value })} placeholder="pcs, set, box..." className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Unit Cost</label>
              <input type="number" step="0.01" value={formData.unit_cost ?? ''} onChange={(event) => setFormData({ ...formData, unit_cost: event.target.value ? Number(event.target.value) : undefined })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Compatible Equipment</label>
              <textarea value={formData.compatible_equipment || ''} onChange={(event) => setFormData({ ...formData, compatible_equipment: event.target.value })} rows={2} placeholder="Equipment, machines, or lines this item applies to" className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
              <textarea value={formData.description || ''} onChange={(event) => setFormData({ ...formData, description: event.target.value })} rows={3} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input type="checkbox" checked={formData.is_active ?? true} onChange={(event) => setFormData({ ...formData, is_active: event.target.checked })} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
              Active catalogue item
            </label>
          </div>
          <div className="mt-4 flex justify-end">
            <button onClick={handleSave} disabled={isSaving} className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50">
              <Save className="w-4 h-4" />
              Save Item
            </button>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input value={filters.search} onChange={(event) => setFilters({ ...filters, search: event.target.value, page: 1 })} placeholder="Search code, name, supplier, or equipment..." className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Type</label>
            <select value={filters.item_type} onChange={(event) => setFilters({ ...filters, item_type: event.target.value as MaintenanceCatalogueItemType | '', page: 1 })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">All Types</option>
              <option value="spare_part">Spare Parts</option>
              <option value="tool">Tools</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category</label>
            <select value={filters.category} onChange={(event) => setFilters({ ...filters, category: event.target.value, page: 1 })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">All Categories</option>
              {categories.map((category) => <option key={category} value={category}>{category}</option>)}
            </select>
          </div>
          <label className="flex items-end gap-2 text-sm text-gray-700 dark:text-gray-300 pb-2">
            <input type="checkbox" checked={filters.include_inactive} onChange={(event) => setFilters({ ...filters, include_inactive: event.target.checked, page: 1 })} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
            Include inactive
          </label>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-600 dark:text-gray-400">Loading catalogue...</div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center text-gray-600 dark:text-gray-400">No catalogue items found</div>
        ) : (
          <div className="grid gap-4 p-4 sm:grid-cols-2 xl:grid-cols-3">
            {items.map((item) => (
              <div key={item.id} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="aspect-[4/3] bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                  {item.image_url ? (
                    <img src={item.image_url} alt={item.name} className="h-full w-full object-cover" />
                  ) : (
                    <ImageIcon className="w-12 h-12 text-gray-400 dark:text-gray-500" />
                  )}
                </div>
                <div className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100 truncate">{item.name}</h2>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{item.item_code}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${item.item_type === 'tool' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300' : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'}`}>
                      {formatType(item.item_type)}
                    </span>
                  </div>
                  {item.description && <p className="mt-3 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{item.description}</p>}
                  <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-gray-600 dark:text-gray-300">
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Category</p>
                      <p className="font-medium text-gray-800 dark:text-gray-100">{item.category || '-'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Location</p>
                      <p className="font-medium text-gray-800 dark:text-gray-100">{item.location || '-'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Supplier</p>
                      <p className="font-medium text-gray-800 dark:text-gray-100">{item.supplier || '-'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Unit Cost</p>
                      <p className="font-medium text-gray-800 dark:text-gray-100">{item.unit_cost != null ? item.unit_cost.toFixed(2) : '-'}</p>
                    </div>
                  </div>
                  {item.compatible_equipment && (
                    <div className="mt-3 text-xs text-gray-600 dark:text-gray-300">
                      <p className="text-gray-500 dark:text-gray-400">Compatible Equipment</p>
                      <p className="mt-1">{item.compatible_equipment}</p>
                    </div>
                  )}
                  <div className="mt-4 flex items-center justify-between">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${item.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}>
                      {item.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <div className="flex items-center gap-2">
                      {canEdit && <button onClick={() => startEdit(item)} className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300">Edit</button>}
                      {canDelete && (
                        <button onClick={() => handleDelete(item)} className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300" title="Deactivate">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <button onClick={() => setFilters({ ...filters, page: Math.max(1, filters.page - 1) })} disabled={filters.page === 1} className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 text-gray-700 dark:text-gray-200">Previous</button>
            <span className="text-sm text-gray-600 dark:text-gray-400">Page {filters.page} of {totalPages}</span>
            <button onClick={() => setFilters({ ...filters, page: Math.min(totalPages, filters.page + 1) })} disabled={filters.page === totalPages} className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 text-gray-700 dark:text-gray-200">Next</button>
          </div>
        )}
      </div>
    </div>
  )
}

export default MaintenanceCataloguePage
