import { AlertTriangle } from 'lucide-react'
import type { InventorySummary, LowStockReport } from '../../services/reports.service'

interface InventoryReportProps {
  summary: InventorySummary
  lowStockReport: LowStockReport | null
}

const InventoryReport = ({ summary, lowStockReport }: InventoryReportProps) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Items</h3>
          <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{summary.total_items}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Value</h3>
          <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">
            ${summary.total_value.toLocaleString()}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Low Stock</h3>
          <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{summary.low_stock_items}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Out of Stock</h3>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400">{summary.out_of_stock}</p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Category</h3>
        <div className="space-y-3">
          {summary.by_category.map((item) => (
            <div key={item.category} className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400 capitalize">{item.category}</span>
              <div className="flex gap-4">
                <span className="text-gray-800 dark:text-gray-100">{item.count} items</span>
                <span className="font-semibold text-gray-800 dark:text-gray-100">
                  ${item.value.toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {lowStockReport && lowStockReport.low_stock_items.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            Low Stock Alert
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Item
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Category
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Quantity
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Reorder Level
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Shortage
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {lowStockReport.low_stock_items.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">{item.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{item.category}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">
                      {item.quantity} {item.unit}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{item.reorder_level}</td>
                    <td className="px-4 py-3 text-sm text-red-600 dark:text-red-400 font-semibold">
                      {item.shortage}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default InventoryReport
