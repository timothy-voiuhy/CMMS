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
      OPERATIONAL: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      MAINTENANCE: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      BREAKDOWN: { color: 'bg-red-100 text-red-800', icon: AlertCircle },
      RETIRED: { color: 'bg-gray-100 text-gray-800', icon: AlertCircle },
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
    <div className="overflow-x-auto bg-white rounded-lg shadow">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Equipment
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ID / Category
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Location
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Manufacturer
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {equipment.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                <Wrench className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p className="text-sm">No equipment found</p>
              </td>
            </tr>
          ) : (
            equipment.map((item) => (
              <tr
                key={item.id}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => onView(item)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Wrench className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">{item.name}</div>
                      {item.model && (
                        <div className="text-xs text-gray-500">Model: {item.model}</div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{item.equipment_id}</div>
                  {item.category && (
                    <div className="text-xs text-gray-500">{item.category}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {item.location ? (
                    <div className="flex items-center text-sm text-gray-900">
                      <MapPin className="w-4 h-4 mr-1 text-gray-400" />
                      {item.location}
                    </div>
                  ) : (
                    <span className="text-sm text-gray-400">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(item.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {item.manufacturer || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onView(item)
                    }}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    View
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onEdit(item)
                    }}
                    className="text-indigo-600 hover:text-indigo-900 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDelete(item)
                    }}
                    className="text-red-600 hover:text-red-900"
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
