import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Save,
  RefreshCw,
  Plus,
  Trash2,
} from 'lucide-react'
import {
  inventoryService,
  type InventoryItem,
  type InventoryCategory,
} from '../../services/inventory.service'
import { Spreadsheet, type SpreadsheetColumn } from '../../components/Spreadsheet'

const InventoryGridPage: React.FC = () => {
  const navigate = useNavigate()
  
  const [items, setItems] = useState<InventoryItem[]>([])
  const [categories, setCategories] = useState<InventoryCategory[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [changedRows, setChangedRows] = useState<Set<number>>(new Set())
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set())

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const [itemsResponse, categoriesResponse] = await Promise.all([
        inventoryService.getAll({ limit: 100 }),
        inventoryService.getCategories(),
      ])
      setItems(itemsResponse.data)
      setCategories(categoriesResponse)
    } catch (error) {
      console.error('Failed to load data:', error)
      alert('Failed to load inventory data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCellChange = (rowIndex: number, columnKey: string, value: any, row: InventoryItem) => {
    setChangedRows((prev) => new Set(prev).add(row.id))
  }

  const handleRowsChange = (newData: InventoryItem[]) => {
    setItems(newData)
  }

  const handleSaveChanges = async () => {
    if (changedRows.size === 0) {
      alert('No changes to save')
      return
    }

    try {
      setIsSaving(true)
      const itemsToUpdate = items.filter((item) => changedRows.has(item.id))
      
      await Promise.all(
        itemsToUpdate.map((item) =>
          inventoryService.update(item.id, {
            name: item.name,
            description: item.description,
            category_id: item.category_id,
            unit_of_measure: item.unit_of_measure,
            min_quantity: item.min_quantity,
            max_quantity: item.max_quantity,
            reorder_point: item.reorder_point,
            unit_cost: item.unit_cost,
            location: item.location,
            supplier: item.supplier,
            notes: item.notes,
          })
        )
      )

      setChangedRows(new Set())
      alert(`Successfully saved ${itemsToUpdate.length} items`)
      await loadData()
    } catch (error) {
      console.error('Failed to save changes:', error)
      alert('Failed to save changes')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedRows.size === 0) {
      alert('Please select rows to delete')
      return
    }

    if (!confirm(`Delete ${selectedRows.size} selected item(s)?`)) {
      return
    }

    try {
      const rowsToDelete = Array.from(selectedRows).map((idx) => items[idx])
      await Promise.all(
        rowsToDelete.map((item) => inventoryService.delete(item.id))
      )
      alert(`Successfully deleted ${rowsToDelete.length} items`)
      setSelectedRows(new Set())
      await loadData()
    } catch (error) {
      console.error('Failed to delete items:', error)
      alert('Failed to delete items')
    }
  }

  const columns: SpreadsheetColumn<InventoryItem>[] = [
    {
      key: 'item_code',
      label: 'Item Code',
      width: 120,
      editable: true,
    },
    {
      key: 'name',
      label: 'Name',
      width: 200,
      editable: true,
    },
    {
      key: 'description',
      label: 'Description',
      width: 250,
      editable: true,
    },
    {
      key: 'category_id',
      label: 'Category',
      width: 150,
      editable: true,
      type: 'select',
      options: categories.map((cat) => ({
        value: cat.id,
        label: cat.name,
      })),
      format: (value) => {
        const cat = categories.find((c) => c.id === value)
        return cat?.name || 'Unknown'
      },
    },
    {
      key: 'quantity',
      label: 'Quantity',
      width: 120,
      editable: true,
      type: 'number',
    },
    {
      key: 'unit_of_measure',
      label: 'Unit',
      width: 100,
      editable: true,
    },
    {
      key: 'min_quantity',
      label: 'Min Qty',
      width: 110,
      editable: true,
      type: 'number',
    },
    {
      key: 'max_quantity',
      label: 'Max Qty',
      width: 110,
      editable: true,
      type: 'number',
    },
    {
      key: 'reorder_point',
      label: 'Reorder Point',
      width: 130,
      editable: true,
      type: 'number',
    },
    {
      key: 'unit_cost',
      label: 'Unit Cost',
      width: 120,
      editable: true,
      type: 'number',
      format: (value) => (value != null ? `$${value.toFixed(2)}` : '-'),
    },
    {
      key: 'location',
      label: 'Location',
      width: 150,
      editable: true,
    },
    {
      key: 'supplier',
      label: 'Supplier',
      width: 150,
      editable: true,
    },
    {
      key: 'batch_number',
      label: 'Batch #',
      width: 120,
      editable: true,
    },
    {
      key: 'notes',
      label: 'Notes',
      width: 200,
      editable: true,
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

  return (
    <div className="p-6 h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/inventory')}
              className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to List
            </button>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Inventory Spreadsheet</h1>
            {changedRows.size > 0 && (
              <span className="px-3 py-1 text-sm bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full">
                {changedRows.size} unsaved change(s)
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={loadData}
              className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            
            <button
              onClick={() => navigate('/inventory/new')}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-green-600 dark:bg-green-500 text-white rounded-lg hover:bg-green-700 dark:hover:bg-green-600"
            >
              <Plus className="w-4 h-4" />
              Add New
            </button>
            
            <button
              onClick={handleDeleteSelected}
              disabled={selectedRows.size === 0}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-red-600 dark:bg-red-500 text-white rounded-lg hover:bg-red-700 dark:hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 className="w-4 h-4" />
              Delete ({selectedRows.size})
            </button>
            
            <button
              onClick={handleSaveChanges}
              disabled={changedRows.size === 0 || isSaving}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-400">
          Excel-like spreadsheet with full keyboard navigation and editing capabilities.
        </p>
      </div>

      {/* Spreadsheet - fills remaining space */}
      <Spreadsheet
        data={items}
        columns={columns}
        onCellChange={handleCellChange}
        onRowsChange={handleRowsChange}
        rowKey="id"
        height="100%"
        enableSelection={true}
        enableKeyboardNav={true}
        enableCopyPaste={true}
        enableExport={true}
        enableImport={false}
        onSelectionChange={setSelectedRows}
        exportFileName="inventory"
        stickyHeader={true}
        showRowNumbers={true}
        rowClassName={(row) => {
          if (row.reorder_point && row.quantity <= row.reorder_point) {
            return 'bg-red-50'
          }
          return ''
        }}
        cellClassName={(value, row, column) => {
          if (column.key === 'quantity' && row.reorder_point && row.quantity <= row.reorder_point) {
            return 'text-red-600 font-semibold'
          }
          return ''
        }}
      />
    </div>
  )
}

export default InventoryGridPage
