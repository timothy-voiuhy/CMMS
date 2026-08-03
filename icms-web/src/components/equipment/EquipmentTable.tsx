import React from 'react'
import type { Equipment } from '../../types'
import { Wrench, MapPin, AlertCircle, CheckCircle, Clock } from 'lucide-react'

interface EquipmentTableProps {
  equipment: Equipment[]
  onView: (equipment: Equipment) => void
  onEdit: (equipment: Equipment) => void
  onDelete: (equipment: Equipment) => void
}

const EquipmentTable: React.FC<EquipmentTableProps> = ({
  equipment,
  onView,
  onEdit,
  onDelete,
}) => {
  const getStatusBadge = (status: string) => {
    const statusConfig = {
      OPERATIONAL: { color: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300', icon: CheckCircle },
      MAINTENANCE: { color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300', icon: Clock },
      BREAKDOWN: { color: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300', icon: AlertCircle },
      RETIRED: { color: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300', icon: AlertCircle },
    }

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.OPERATIONAL
    const Icon = config.icon

    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3" />
        {status}
      </span>
    )
  }

  return (
    <div className="overflow-x-auto bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Equipment
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              ID / Category
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Location
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Manufacturer
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          {equipment.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                <Wrench className="w-12 h-12 mx-auto mb-3 text-gray-400 dark:text-gray-500" />
                <p className="text-sm">No equipment found</p>
              </td>
            </tr>
          ) : (
            equipment.map((item) => (
              <tr
                key={item.id}
                className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                onClick={() => onView(item)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                      <Wrench className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{item.name}</div>
                      {item.model && (
                        <div className="text-xs text-gray-500 dark:text-gray-400">Model: {item.model}</div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900 dark:text-gray-100">{item.equipment_id}</div>
                  {item.category && (
                    <div className="text-xs text-gray-500 dark:text-gray-400">{item.category}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {item.location ? (
                    <div className="flex items-center text-sm text-gray-900 dark:text-gray-100">
                      <MapPin className="w-4 h-4 mr-1 text-gray-400 dark:text-gray-500" />
                      {item.location}
                    </div>
                  ) : (
                    <span className="text-sm text-gray-400 dark:text-gray-500">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(item.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {item.manufacturer || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onView(item)
                    }}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 mr-3"
                  >
                    View
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onEdit(item)
                    }}
                    className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-900 dark:hover:text-indigo-300 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDelete(item)
                    }}
                    className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export default EquipmentTable
