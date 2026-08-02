import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import * as XLSX from 'xlsx'
import {
  Download,
  Upload,
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

interface CellPosition {
  row: number
  col: number
}

const InventoryGridPage: React.FC = () => {
  const navigate = useNavigate()
  const tableRef = useRef<HTMLDivElement>(null)
  
  const [items, setItems] = useState<InventoryItem[]>([])
  const [categories, setCategories] = useState<InventoryCategory[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [changedRows, setChangedRows] = useState<Set<number>>(new Set())
  const [selectedCell, setSelectedCell] = useState<CellPosition | null>(null)
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set())
  const [editingCell, setEditingCell] = useState<CellPosition | null>(null)
  const [copiedData, setCopiedData] = useState<string | null>(null)

  const columns = [
    { key: 'item_code', label: 'Item Code', width: 120, editable: true },
    { key: 'name', label: 'Name', width: 200, editable: true },
    { key: 'description', label: 'Description', width: 250, editable: true },
    { key: 'category_id', label: 'Category', width: 150, editable: true, type: 'select' },
    { key: 'quantity', label: 'Quantity', width: 120, editable: true, type: 'number' },
    { key: 'unit_of_measure', label: 'Unit', width: 100, editable: true },
    { key: 'min_quantity', label: 'Min Qty', width: 110, editable: true, type: 'number' },
    { key: 'max_quantity', label: 'Max Qty', width: 110, editable: true, type: 'number' },
    { key: 'reorder_point', label: 'Reorder Point', width: 130, editable: true, type: 'number' },
    { key: 'unit_cost', label: 'Unit Cost', width: 120, editable: true, type: 'number' },
    { key: 'location', label: 'Location', width: 150, editable: true },
    { key: 'supplier', label: 'Supplier', width: 150, editable: true },
    { key: 'batch_number', label: 'Batch #', width: 120, editable: true },
    { key: 'notes', label: 'Notes', width: 200, editable: true },
  ]

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!selectedCell) return

      // Copy (Ctrl+C)
      if (e.ctrlKey && e.key === 'c') {
        const item = items[selectedCell.row]
        const column = columns[selectedCell.col]
        const value = item[column.key as keyof InventoryItem]
        setCopiedData(String(value || ''))
        e.preventDefault()
      }

      // Paste (Ctrl+V)
      if (e.ctrlKey && e.key === 'v' && copiedData) {
        handleCellEdit(selectedCell.row, columns[selectedCell.col].key, copiedData)
        e.preventDefault()
      }

      // Delete
      if (e.key === 'Delete' && !editingCell) {
        handleCellEdit(selectedCell.row, columns[selectedCell.col].key, '')
      }

      // Enter - start editing
      if (e.key === 'Enter' && !editingCell) {
        setEditingCell(selectedCell)
        e.preventDefault()
      }

      // Escape - cancel editing
      if (e.key === 'Escape' && editingCell) {
        setEditingCell(null)
      }

      // Arrow navigation
      if (!editingCell) {
        let newRow = selectedCell.row
        let newCol = selectedCell.col

        if (e.key === 'ArrowUp' && newRow > 0) newRow--
        if (e.key === 'ArrowDown' && newRow < items.length - 1) newRow++
        if (e.key === 'ArrowLeft' && newCol > 0) newCol--
        if (e.key === 'ArrowRight' && newCol < columns.length - 1) newCol++

        if (newRow !== selectedCell.row || newCol !== selectedCell.col) {
          setSelectedCell({ row: newRow, col: newCol })
          e.preventDefault()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedCell, editingCell, copiedData, items])

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

  const handleCellEdit = (rowIndex: number, columnKey: string, value: any) => {
    const newItems = [...items]
    newItems[rowIndex] = {
      ...newItems[rowIndex],
      [columnKey]: value,
    }
    setItems(newItems)
    setChangedRows((prev) => new Set(prev).add(newItems[rowIndex].id))
  }

  const handleCellClick = (rowIndex: number, colIndex: number) => {
    setSelectedCell({ row: rowIndex, col: colIndex })
    setEditingCell(null)
  }

  const handleCellDoubleClick = (rowIndex: number, colIndex: number) => {
    if (columns[colIndex].editable) {
      setEditingCell({ row: rowIndex, col: colIndex })
      setSelectedCell({ row: rowIndex, col: colIndex })
    }
  }

  const handleRowSelect = (rowIndex: number, isCtrlKey: boolean) => {
    if (isCtrlKey) {
      const newSelected = new Set(selectedRows)
      if (newSelected.has(rowIndex)) {
        newSelected.delete(rowIndex)
      } else {
        newSelected.add(rowIndex)
      }
      setSelectedRows(newSelected)
    } else {
      setSelectedRows(new Set([rowIndex]))
    }
  }

  const getCategoryName = (categoryId: number) => {
    return categories.find((c) => c.id === categoryId)?.name || 'Unknown'
  }

  const formatCellValue = (item: InventoryItem, column: typeof columns[0]) => {
    const value = item[column.key as keyof InventoryItem]
    
    if (column.key === 'category_id') {
      return getCategoryName(value as number)
    }
    
    if (column.type === 'number' && value != null) {
      return typeof value === 'number' ? value.toFixed(2) : value
    }
    
    return value || ''
  }

  const isLowStock = (item: InventoryItem) => {
    return item.reorder_point && item.quantity <= item.reorder_point
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

  const handleExportToExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(
      items.map((item) => ({
        'Item Code': item.item_code,
        'Name': item.name,
        'Description': item.description || '',
        'Category': getCategoryName(item.category_id),
        'Quantity': item.quantity,
        'Unit': item.unit_of_measure,
        'Min Quantity': item.min_quantity || '',
        'Max Quantity': item.max_quantity || '',
        'Reorder Point': item.reorder_point || '',
        'Unit Cost': item.unit_cost || '',
        'Location': item.location || '',
        'Supplier': item.supplier || '',
        'Batch Number': item.batch_number || '',
        'Notes': item.notes || '',
      }))
    )

    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Inventory')
    XLSX.writeFile(workbook, `inventory_${new Date().toISOString().split('T')[0]}.xlsx`)
  }

  const handleImportFromExcel = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target?.result as ArrayBuffer)
        const workbook = XLSX.read(data, { type: 'array' })
        const worksheet = workbook.Sheets[workbook.SheetNames[0]]
        const jsonData = XLSX.utils.sheet_to_json(worksheet)

        console.log('Imported data:', jsonData)
        alert(`Imported ${jsonData.length} rows. Import functionality coming soon!`)
        // TODO: Implement import logic with validation
      } catch (error) {
        console.error('Failed to import Excel:', error)
        alert('Failed to import Excel file')
      }
    }
    reader.readAsArrayBuffer(file)
    event.target.value = '' // Reset input
  }

  const handleAddRow = () => {
    navigate('/inventory/new')
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6 h-screen flex flex-col">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/inventory')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to List
            </button>
            <h1 className="text-2xl font-bold text-gray-800">Inventory Spreadsheet</h1>
            {changedRows.size > 0 && (
              <span className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-full">
                {changedRows.size} unsaved change(s)
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={loadData}
              className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            
            <button
              onClick={handleAddRow}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Plus className="w-4 h-4" />
              Add New
            </button>
            
            <button
              onClick={handleDeleteSelected}
              disabled={selectedRows.size === 0}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 className="w-4 h-4" />
              Delete ({selectedRows.size})
            </button>
            
            <label className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer">
              <Upload className="w-4 h-4" />
              Import Excel
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleImportFromExcel}
                className="hidden"
              />
            </label>
            
            <button
              onClick={handleExportToExcel}
              className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Download className="w-4 h-4" />
              Export Excel
            </button>
            
            <button
              onClick={handleSaveChanges}
              disabled={changedRows.size === 0 || isSaving}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
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

        <p className="text-sm text-gray-600">
          Custom spreadsheet with full editing. Double-click cells to edit, use arrow keys to navigate.
        </p>
      </div>

      {/* Custom Spreadsheet */}
      <div ref={tableRef} className="flex-1 overflow-auto border border-gray-300 rounded-lg bg-white">
        <table className="min-w-full border-collapse">
          <thead className="sticky top-0 bg-gray-100 z-10">
            <tr>
              <th className="border border-gray-300 px-2 py-2 text-xs font-semibold text-gray-700 w-12">
                #
              </th>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="border border-gray-300 px-2 py-2 text-xs font-semibold text-gray-700 text-left"
                  style={{ minWidth: column.width }}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item, rowIndex) => (
              <tr
                key={item.id}
                className={`hover:bg-blue-50 ${selectedRows.has(rowIndex) ? 'bg-blue-100' : ''} ${
                  isLowStock(item) ? 'bg-red-50' : ''
                }`}
              >
                <td
                  className="border border-gray-300 px-2 py-1 text-xs text-center cursor-pointer"
                  onClick={(e) => handleRowSelect(rowIndex, e.ctrlKey || e.metaKey)}
                >
                  <input
                    type="checkbox"
                    checked={selectedRows.has(rowIndex)}
                    onChange={(e) => handleRowSelect(rowIndex, e.ctrlKey || e.metaKey)}
                    className="cursor-pointer"
                  />
                </td>
                {columns.map((column, colIndex) => {
                  const isSelected = selectedCell?.row === rowIndex && selectedCell?.col === colIndex
                  const isEditing = editingCell?.row === rowIndex && editingCell?.col === colIndex

                  return (
                    <td
                      key={column.key}
                      className={`border border-gray-300 px-2 py-1 text-xs ${
                        isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                      } ${column.editable ? 'cursor-cell' : 'cursor-default'}`}
                      onClick={() => handleCellClick(rowIndex, colIndex)}
                      onDoubleClick={() => handleCellDoubleClick(rowIndex, colIndex)}
                      style={{ minWidth: column.width }}
                    >
                      {isEditing ? (
                        column.type === 'select' ? (
                          <select
                            autoFocus
                            value={item[column.key as keyof InventoryItem] as any}
                            onChange={(e) => {
                              handleCellEdit(rowIndex, column.key, parseInt(e.target.value))
                              setEditingCell(null)
                            }}
                            onBlur={() => setEditingCell(null)}
                            className="w-full px-1 py-0 text-xs border-0 focus:ring-2 focus:ring-blue-500 outline-none"
                          >
                            {categories.map((cat) => (
                              <option key={cat.id} value={cat.id}>
                                {cat.name}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <input
                            autoFocus
                            type={column.type === 'number' ? 'number' : 'text'}
                            step={column.type === 'number' ? '0.01' : undefined}
                            value={(item[column.key as keyof InventoryItem] as any) || ''}
                            onChange={(e) => {
                              const value = column.type === 'number' 
                                ? (e.target.value ? parseFloat(e.target.value) : null)
                                : e.target.value
                              handleCellEdit(rowIndex, column.key, value)
                            }}
                            onBlur={() => setEditingCell(null)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                setEditingCell(null)
                                if (rowIndex < items.length - 1) {
                                  setSelectedCell({ row: rowIndex + 1, col: colIndex })
                                }
                              }
                              if (e.key === 'Escape') {
                                setEditingCell(null)
                              }
                            }}
                            className="w-full px-1 py-0 text-xs border-0 focus:ring-2 focus:ring-blue-500 outline-none"
                          />
                        )
                      ) : (
                        <div className="truncate">
                          {formatCellValue(item, column)}
                        </div>
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Help Text */}
      <div className="mt-2 text-xs text-gray-600 flex items-center gap-4">
        <span>💡 Double-click to edit • Arrow keys to navigate • Enter to edit • Ctrl+C to copy • Ctrl+V to paste • Delete to clear</span>
        {copiedData && <span className="text-green-600">✓ Copied: {copiedData.substring(0, 20)}...</span>}
      </div>
    </div>
  )
}

export default InventoryGridPage
