import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Package,
  Edit,
  Trash2,
  Plus,
  Minus,
  History,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'
import {
  inventoryService,
  type InventoryItem,
  type InventoryTransaction,
  type TransactionType,
} from '../../services/inventory.service'

const InventoryDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [item, setItem] = useState<InventoryItem | null>(null)
  const [transactions, setTransactions] = useState<InventoryTransaction[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'transactions'>('overview')
  const [showAdjustModal, setShowAdjustModal] = useState(false)
  const [adjustData, setAdjustData] = useState({
    quantity: 0,
    transaction_type: 'receipt' as TransactionType,
    notes: '',
    reference: '',
  })

  useEffect(() => {
    if (id && id !== 'new') {
      loadItem()
      loadTransactions()
    }
  }, [id])

  const loadItem = async () => {
    if (!id || id === 'new') return

    const itemId = parseInt(id)
    if (isNaN(itemId)) {
      navigate('/inventory')
      return
    }

    try {
      setIsLoading(true)
      const data = await inventoryService.getById(itemId)
      setItem(data)
    } catch (error) {
      console.error('Failed to load item:', error)
      alert('Failed to load item details')
    } finally {
      setIsLoading(false)
    }
  }

  const loadTransactions = async () => {
    if (!id || id === 'new') return

    const itemId = parseInt(id)
    if (isNaN(itemId)) return

    try {
      const data = await inventoryService.getTransactions(itemId)
      setTransactions(data)
    } catch (error) {
      console.error('Failed to load transactions:', error)
    }
  }

  const handleDelete = async () => {
    if (!id || !item) return

    if (!confirm(`Are you sure you want to delete ${item.name}?`)) return

    try {
      await inventoryService.delete(parseInt(id))
      navigate('/inventory')
    } catch (error) {
      console.error('Failed to delete item:', error)
      alert('Failed to delete item')
    }
  }

  const handleAdjustQuantity = async () => {
    if (!id) return

    try {
      await inventoryService.adjustQuantity(parseInt(id), adjustData)
      setShowAdjustModal(false)
      setAdjustData({
        quantity: 0,
        transaction_type: 'receipt',
        notes: '',
        reference: '',
      })
      loadItem()
      loadTransactions()
    } catch (error: any) {
      console.error('Failed to adjust quantity:', error)
      const detail = error.response?.data?.detail
      alert(typeof detail === 'string' ? detail : 'Failed to adjust quantity')
    }
  }

  const getStockStatus = () => {
    if (!item) return 'unknown'
    if (item.quantity <= 0) return 'out-of-stock'
    if (item.reorder_point && item.quantity <= item.reorder_point) return 'low-stock'
    return 'in-stock'
  }

  const getStockBadge = () => {
    const status = getStockStatus()
    if (status === 'out-of-stock') {
      return (
        <span className="px-3 py-1 text-sm font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 rounded-full">
          Out of Stock
        </span>
      )
    }
    if (status === 'low-stock') {
      return (
        <span className="px-3 py-1 text-sm font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 rounded-full">
          Low Stock
        </span>
      )
    }
    return (
      <span className="px-3 py-1 text-sm font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 rounded-full">
        In Stock
      </span>
    )
  }

  const formatCategory = (category: string) => {
    return category
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const formatTransactionType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  const getTransactionIcon = (type: TransactionType) => {
    if (type === 'receipt' || type === 'return') {
      return <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400" />
    }
    return <TrendingDown className="w-4 h-4 text-red-600 dark:text-red-400" />
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

  if (!item) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-gray-500 dark:text-gray-400">Item not found</p>
          <button
            onClick={() => navigate('/inventory')}
            className="mt-4 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-500"
          >
            Back to Inventory
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/inventory')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Inventory
        </button>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 h-16 w-16 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <Package className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{item.name}</h1>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
                  <span>Code: {item.item_code}</span>
                  <span>• {formatCategory(item.category)}</span>
                </div>
                <div className="mt-2">{getStockBadge()}</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowAdjustModal(true)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 dark:bg-green-500 border border-green-600 dark:border-green-500 rounded-lg hover:bg-green-700 dark:hover:bg-green-600"
              >
                <Plus className="w-4 h-4" />
                Adjust Qty
              </button>
              <button
                onClick={() => navigate(`/inventory/${id}/edit`)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={handleDelete}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-white dark:bg-gray-700 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: Package },
              { id: 'transactions', label: 'Transaction History', icon: History },
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow p-6">
        {activeTab === 'overview' && (
          <div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
              {/* Stock Information */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Stock Information</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Current Quantity:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {item.quantity} {item.unit_of_measure}
                    </span>
                  </div>
                  {item.reorder_point && (
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Reorder Point:</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {item.reorder_point} {item.unit_of_measure}
                      </span>
                    </div>
                  )}
                  {item.min_quantity && (
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Min Quantity:</span>
                      <span className="text-sm text-gray-900">
                        {item.min_quantity} {item.unit_of_measure}
                      </span>
                    </div>
                  )}
                  {item.max_quantity && (
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Max Quantity:</span>
                      <span className="text-sm text-gray-900">
                        {item.max_quantity} {item.unit_of_measure}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Costing */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Costing</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Unit Cost:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {item.unit_cost ? `$${item.unit_cost.toFixed(2)}` : '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total Value:</span>
                    <span className="text-sm font-semibold text-green-600">
                      {item.unit_cost
                        ? `$${(item.quantity * item.unit_cost).toFixed(2)}`
                        : '-'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Location & Supplier */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">
                  Location & Supplier
                </h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Location:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {item.location || '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Supplier:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {item.supplier || '-'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Details */}
            <div className="space-y-4">
              {item.description && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase mb-2">Description</h3>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{item.description}</p>
                </div>
              )}

              {(item.batch_number || item.expiry_date) && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase mb-2">
                    Batch Information
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    {item.batch_number && (
                      <div>
                        <span className="text-sm text-gray-600 dark:text-gray-400">Batch Number: </span>
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{item.batch_number}</span>
                      </div>
                    )}
                    {item.expiry_date && (
                      <div>
                        <span className="text-sm text-gray-600 dark:text-gray-400">Expiry Date: </span>
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {new Date(item.expiry_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {item.notes && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase mb-2">Notes</h3>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{item.notes}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'transactions' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Transaction History</h3>
            {transactions.length === 0 ? (
              <div className="text-center py-8">
                <History className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400">No transactions recorded</p>
              </div>
            ) : (
              <div className="space-y-3">
                {transactions.map((txn) => (
                  <div
                    key={txn.id}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      {getTransactionIcon(txn.transaction_type)}
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">
                          {formatTransactionType(txn.transaction_type)}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {new Date(txn.created_at).toLocaleString()}
                        </p>
                        {txn.notes && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{txn.notes}</p>}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900 dark:text-gray-100">
                        {txn.quantity > 0 ? '+' : ''}
                        {txn.quantity} {item.unit_of_measure}
                      </p>
                      {txn.reference_number && (
                        <p className="text-sm text-gray-500 dark:text-gray-400">Ref: {txn.reference_number}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Adjust Quantity Modal */}
      {showAdjustModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Adjust Quantity</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Transaction Type <span className="text-red-500">*</span>
                </label>
                <select
                  value={adjustData.transaction_type}
                  onChange={(e) =>
                    setAdjustData({ ...adjustData, transaction_type: e.target.value as TransactionType })
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="receipt">Receipt (Add)</option>
                  <option value="issue">Issue (Remove)</option>
                  <option value="return">Return (Add)</option>
                  <option value="adjustment">Adjustment</option>
                  <option value="scrap">Scrap (Remove)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Quantity <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={adjustData.quantity}
                  onChange={(e) =>
                    setAdjustData({ ...adjustData, quantity: parseFloat(e.target.value) || 0 })
                  }
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Enter quantity"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Reference Number</label>
                <input
                  type="text"
                  value={adjustData.reference}
                  onChange={(e) => setAdjustData({ ...adjustData, reference: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="PO number, WO number, etc."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Notes</label>
                <textarea
                  value={adjustData.notes}
                  onChange={(e) => setAdjustData({ ...adjustData, notes: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="Transaction notes..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => {
                  setShowAdjustModal(false)
                  setAdjustData({
                    quantity: 0,
                    transaction_type: 'receipt',
                    notes: '',
                    reference: '',
                  })
                }}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleAdjustQuantity}
                className="px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
              >
                Adjust Quantity
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InventoryDetailPage
