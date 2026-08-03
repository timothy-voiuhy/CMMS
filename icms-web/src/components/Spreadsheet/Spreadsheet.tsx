import React, { useState, useEffect, useRef, useCallback } from 'react'
import * as XLSX from 'xlsx'
import { Download, Upload } from 'lucide-react'

export interface SpreadsheetColumn<T = any> {
  key: string
  label: string
  width?: number
  editable?: boolean
  type?: 'text' | 'number' | 'select' | 'date'
  options?: Array<{ value: any; label: string }> // For select type
  render?: (value: any, row: T) => React.ReactNode
  format?: (value: any, row: T) => string
  validate?: (value: any, row: T) => boolean | string
}

export interface SpreadsheetProps<T = any> {
  data: T[]
  columns: SpreadsheetColumn<T>[]
  onCellChange?: (rowIndex: number, columnKey: string, value: any, row: T) => void
  onRowsChange?: (newData: T[]) => void
  rowKey?: keyof T | ((row: T) => string | number)
  height?: string
  maxHeight?: string
  enableSelection?: boolean
  enableKeyboardNav?: boolean
  enableCopyPaste?: boolean
  enableExport?: boolean
  enableImport?: boolean
  onSelectionChange?: (selectedRows: Set<number>) => void
  rowClassName?: (row: T, rowIndex: number) => string
  cellClassName?: (value: any, row: T, column: SpreadsheetColumn<T>) => string
  readOnly?: boolean
  stickyHeader?: boolean
  showRowNumbers?: boolean
  exportFileName?: string
}

interface CellPosition {
  row: number
  col: number
}

function Spreadsheet<T = any>({
  data,
  columns,
  onCellChange,
  onRowsChange,
  rowKey = 'id',
  height,
  maxHeight = '600px',
  enableSelection = true,
  enableKeyboardNav = true,
  enableCopyPaste = true,
  enableExport = true,
  enableImport = false,
  onSelectionChange,
  rowClassName,
  cellClassName,
  readOnly = false,
  stickyHeader = true,
  showRowNumbers = true,
  exportFileName = 'spreadsheet',
}: SpreadsheetProps<T>) {
  const [selectedCell, setSelectedCell] = useState<CellPosition | null>(null)
  const [editingCell, setEditingCell] = useState<CellPosition | null>(null)
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set())
  const [copiedData, setCopiedData] = useState<string | null>(null)
  const tableRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  // Get row key
  const getRowKey = useCallback((row: T, index: number): string | number => {
    if (typeof rowKey === 'function') {
      return rowKey(row)
    }
    return (row[rowKey] as any) ?? index
  }, [rowKey])

  // Handle cell click
  const handleCellClick = useCallback((rowIndex: number, colIndex: number) => {
    setSelectedCell({ row: rowIndex, col: colIndex })
    setEditingCell(null)
  }, [])

  // Handle cell double click
  const handleCellDoubleClick = useCallback((rowIndex: number, colIndex: number) => {
    if (readOnly) return
    const column = columns[colIndex]
    if (column.editable !== false) {
      setEditingCell({ row: rowIndex, col: colIndex })
      setSelectedCell({ row: rowIndex, col: colIndex })
    }
  }, [columns, readOnly])

  // Handle cell edit
  const handleCellEdit = useCallback((rowIndex: number, columnKey: string, value: any) => {
    const newData = [...data]
    const row = newData[rowIndex]
    const column = columns.find(c => c.key === columnKey)

    // Validate
    if (column?.validate) {
      const validation = column.validate(value, row)
      if (validation !== true) {
        alert(typeof validation === 'string' ? validation : 'Invalid value')
        return
      }
    }

    // Update row
    newData[rowIndex] = {
      ...row,
      [columnKey]: value,
    }

    // Notify parent
    if (onCellChange) {
      onCellChange(rowIndex, columnKey, value, newData[rowIndex])
    }
    if (onRowsChange) {
      onRowsChange(newData)
    }
  }, [data, columns, onCellChange, onRowsChange])

  // Handle row selection
  const handleRowSelect = useCallback((rowIndex: number, isCtrlKey: boolean) => {
    if (!enableSelection) return

    let newSelected: Set<number>
    if (isCtrlKey) {
      newSelected = new Set(selectedRows)
      if (newSelected.has(rowIndex)) {
        newSelected.delete(rowIndex)
      } else {
        newSelected.add(rowIndex)
      }
    } else {
      newSelected = new Set([rowIndex])
    }
    
    setSelectedRows(newSelected)
    if (onSelectionChange) {
      onSelectionChange(newSelected)
    }
  }, [enableSelection, selectedRows, onSelectionChange])

  // Format cell value
  const formatCellValue = useCallback((value: any, row: T, column: SpreadsheetColumn<T>) => {
    if (column.format) {
      return column.format(value, row)
    }
    
    if (column.type === 'select' && column.options) {
      const option = column.options.find(opt => opt.value === value)
      return option?.label || String(value || '')
    }
    
    if (column.type === 'number' && value != null) {
      return typeof value === 'number' ? value.toFixed(2) : value
    }
    
    if (column.type === 'date' && value) {
      return new Date(value).toLocaleDateString()
    }
    
    return value || ''
  }, [])

  // Render cell content
  const renderCellContent = useCallback((value: any, row: T, column: SpreadsheetColumn<T>) => {
    if (column.render) {
      return column.render(value, row)
    }
    return formatCellValue(value, row, column)
  }, [formatCellValue])

  // Keyboard navigation
  useEffect(() => {
    if (!enableKeyboardNav) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (!selectedCell) return

      // Copy (Ctrl+C)
      if (enableCopyPaste && e.ctrlKey && e.key === 'c') {
        const row = data[selectedCell.row]
        const column = columns[selectedCell.col]
        const value = (row as any)[column.key]
        setCopiedData(String(value || ''))
        e.preventDefault()
      }

      // Paste (Ctrl+V)
      if (enableCopyPaste && e.ctrlKey && e.key === 'v' && copiedData && !readOnly) {
        handleCellEdit(selectedCell.row, columns[selectedCell.col].key, copiedData)
        e.preventDefault()
      }

      // Delete
      if (e.key === 'Delete' && !editingCell && !readOnly) {
        handleCellEdit(selectedCell.row, columns[selectedCell.col].key, '')
      }

      // Enter - start editing or move down
      if (e.key === 'Enter') {
        if (!editingCell && !readOnly) {
          setEditingCell(selectedCell)
        } else if (editingCell) {
          setEditingCell(null)
          if (selectedCell.row < data.length - 1) {
            setSelectedCell({ row: selectedCell.row + 1, col: selectedCell.col })
          }
        }
        e.preventDefault()
      }

      // Tab - move right or to next row
      if (e.key === 'Tab') {
        if (editingCell) {
          setEditingCell(null)
        }
        let newRow = selectedCell.row
        let newCol = selectedCell.col + 1
        if (newCol >= columns.length) {
          newCol = 0
          newRow = Math.min(selectedCell.row + 1, data.length - 1)
        }
        setSelectedCell({ row: newRow, col: newCol })
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
        if (e.key === 'ArrowDown' && newRow < data.length - 1) newRow++
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
  }, [
    selectedCell,
    editingCell,
    copiedData,
    data,
    columns,
    enableKeyboardNav,
    enableCopyPaste,
    readOnly,
    handleCellEdit,
  ])

  // Auto-focus input when editing
  useEffect(() => {
    if (editingCell && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [editingCell])

  // Export to Excel
  const handleExport = useCallback(() => {
    const exportData = data.map(row => {
      const exportRow: any = {}
      columns.forEach(col => {
        const value = (row as any)[col.key]
        exportRow[col.label] = formatCellValue(value, row, col)
      })
      return exportRow
    })

    const worksheet = XLSX.utils.json_to_sheet(exportData)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1')
    XLSX.writeFile(workbook, `${exportFileName}_${new Date().toISOString().split('T')[0]}.xlsx`)
  }, [data, columns, exportFileName, formatCellValue])

  // Import from Excel
  const handleImport = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const arrayBuffer = new Uint8Array(e.target?.result as ArrayBuffer)
        const workbook = XLSX.read(arrayBuffer, { type: 'array' })
        const worksheet = workbook.Sheets[workbook.SheetNames[0]]
        const jsonData = XLSX.utils.sheet_to_json(worksheet)

        console.log('Imported data:', jsonData)
        alert(`Imported ${jsonData.length} rows. Process the data in onImport callback.`)
        // Parent component should handle the imported data
      } catch (error) {
        console.error('Failed to import Excel:', error)
        alert('Failed to import Excel file')
      }
    }
    reader.readAsArrayBuffer(file)
    event.target.value = ''
  }, [])

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      {(enableExport || enableImport) && (
        <div className="flex items-center gap-2 mb-2 flex-shrink-0">
          {enableExport && (
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          )}
          {enableImport && (
            <label className="flex items-center gap-2 px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
              <Upload className="w-4 h-4" />
              Import
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleImport}
                className="hidden"
              />
            </label>
          )}
          {enableCopyPaste && copiedData && (
            <span className="text-xs text-green-600">
              ✓ Copied: {copiedData.substring(0, 30)}...
            </span>
          )}
        </div>
      )}

      {/* Spreadsheet */}
      <div
        ref={tableRef}
        className="overflow-auto border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 flex-1"
        style={height ? { height } : maxHeight ? { maxHeight } : {}}
      >
        <table className="min-w-full border-collapse">
          <thead className={stickyHeader ? 'sticky top-0 bg-gray-100 dark:bg-gray-700 z-10' : 'bg-gray-100 dark:bg-gray-700'}>
            <tr>
              {showRowNumbers && (
                <th className="border border-gray-300 dark:border-gray-600 px-2 py-2 text-xs font-semibold text-gray-700 dark:text-gray-300 w-12 bg-gray-200 dark:bg-gray-600">
                  #
                </th>
              )}
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="border border-gray-300 dark:border-gray-600 px-2 py-2 text-xs font-semibold text-gray-700 dark:text-gray-300 text-left bg-gray-100 dark:bg-gray-700"
                  style={{ minWidth: column.width || 120 }}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr
                key={getRowKey(row, rowIndex)}
                className={`hover:bg-blue-50 dark:hover:bg-blue-900/20 ${
                  selectedRows.has(rowIndex) ? 'bg-blue-100 dark:bg-blue-900/30' : ''
                } ${rowClassName ? rowClassName(row, rowIndex) : ''}`}
              >
                {showRowNumbers && (
                  <td
                    className="border border-gray-300 dark:border-gray-600 px-2 py-1 text-xs text-center cursor-pointer bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                    onClick={(e) => handleRowSelect(rowIndex, e.ctrlKey || e.metaKey)}
                  >
                    {enableSelection ? (
                      <input
                        type="checkbox"
                        checked={selectedRows.has(rowIndex)}
                        onChange={() => {}}
                        className="cursor-pointer"
                      />
                    ) : (
                      rowIndex + 1
                    )}
                  </td>
                )}
                {columns.map((column, colIndex) => {
                  const value = (row as any)[column.key]
                  const isSelected = selectedCell?.row === rowIndex && selectedCell?.col === colIndex
                  const isEditing = editingCell?.row === rowIndex && editingCell?.col === colIndex
                  const isEditable = !readOnly && column.editable !== false

                  return (
                    <td
                      key={column.key}
                      className={`border border-gray-300 dark:border-gray-600 px-2 py-1 text-xs text-gray-900 dark:text-gray-100 ${
                        isSelected ? 'ring-2 ring-inset ring-blue-500 dark:ring-blue-400 bg-blue-50 dark:bg-blue-900/20' : ''
                      } ${isEditable ? 'cursor-cell' : 'cursor-default'} ${
                        cellClassName ? cellClassName(value, row, column) : ''
                      }`}
                      onClick={() => handleCellClick(rowIndex, colIndex)}
                      onDoubleClick={() => handleCellDoubleClick(rowIndex, colIndex)}
                      style={{ minWidth: column.width || 120 }}
                    >
                      {isEditing ? (
                        column.type === 'select' && column.options ? (
                          <select
                            autoFocus
                            value={value ?? ''}
                            onChange={(e) => {
                              const newValue = e.target.value
                              handleCellEdit(rowIndex, column.key, newValue)
                              setEditingCell(null)
                            }}
                            onBlur={() => setEditingCell(null)}
                            className="w-full px-1 py-0 text-xs border-0 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 outline-none"
                          >
                            {column.options.map((opt) => (
                              <option key={String(opt.value)} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <input
                            ref={inputRef}
                            autoFocus
                            type={column.type === 'number' ? 'number' : column.type === 'date' ? 'date' : 'text'}
                            step={column.type === 'number' ? '0.01' : undefined}
                            value={value ?? ''}
                            onChange={(e) => {
                              const newValue = column.type === 'number'
                                ? e.target.value ? parseFloat(e.target.value) : null
                                : e.target.value
                              handleCellEdit(rowIndex, column.key, newValue)
                            }}
                            onBlur={() => setEditingCell(null)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                setEditingCell(null)
                                if (rowIndex < data.length - 1) {
                                  setSelectedCell({ row: rowIndex + 1, col: colIndex })
                                }
                              }
                              if (e.key === 'Escape') {
                                setEditingCell(null)
                              }
                            }}
                            className="w-full px-1 py-0 text-xs border-0 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 outline-none"
                          />
                        )
                      ) : (
                        <div className="truncate">
                          {renderCellContent(value, row, column)}
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

      {/* Help text */}
      {enableKeyboardNav && (
        <div className="mt-2 text-xs text-gray-500 flex-shrink-0">
          💡 Double-click to edit • Arrow keys to navigate • Enter to edit • Tab to move • 
          {enableCopyPaste && ' Ctrl+C/V to copy/paste •'}
          {!readOnly && ' Delete to clear'}
        </div>
      )}
    </div>
  )
}

export default Spreadsheet
