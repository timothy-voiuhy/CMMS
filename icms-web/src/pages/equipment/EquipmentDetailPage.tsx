import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Wrench,
  MapPin,
  Calendar,
  FileText,
  Users,
  Activity,
  Edit,
  Trash2,
  Plus,
  X,
} from 'lucide-react'
import type { Equipment } from '../../types'
import {
  equipmentService,
  type EquipmentOperator,
} from '../../services/equipment.service'
import { craftsmanService } from '../../services/craftsman.service'

const EquipmentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [equipment, setEquipment] = useState<Equipment | null>(null)
  const [operators, setOperators] = useState<EquipmentOperator[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'operators' | 'maintenance' | 'history'>(
    'overview'
  )
  const [isAddingOperator, setIsAddingOperator] = useState(false)
  const [availableCraftsmen, setAvailableCraftsmen] = useState<any[]>([])
  const [selectedCraftsmanId, setSelectedCraftsmanId] = useState<number | null>(null)

  // Load equipment details
  const loadEquipment = async () => {
    if (!id || id === 'new') return

    const equipmentId = parseInt(id)
    if (isNaN(equipmentId)) {
      navigate('/equipment')
      return
    }

    try {
      setIsLoading(true)
      const data = await equipmentService.getById(equipmentId)
      setEquipment(data)
    } catch (error) {
      console.error('Failed to load equipment:', error)
      alert('Failed to load equipment details')
    } finally {
      setIsLoading(false)
    }
  }

  // Load operators
  const loadOperators = async () => {
    if (!id || id === 'new') return

    const equipmentId = parseInt(id)
    if (isNaN(equipmentId)) return

    try {
      const data = await equipmentService.getOperators(equipmentId)
      setOperators(data)
    } catch (error) {
      console.error('Failed to load operators:', error)
    }
  }

  // Load available craftsmen
  const loadAvailableCraftsmen = async () => {
    try {
      const response = await craftsmanService.getAll({ limit: 100 })
      setAvailableCraftsmen(response.data)
    } catch (error) {
      console.error('Failed to load craftsmen:', error)
    }
  }

  useEffect(() => {
    loadEquipment()
    loadOperators()
  }, [id])

  // Handle assign operator
  const handleAssignOperator = async () => {
    if (!id || !selectedCraftsmanId) return

    try {
      await equipmentService.assignOperator(parseInt(id), selectedCraftsmanId)
      setIsAddingOperator(false)
      setSelectedCraftsmanId(null)
      loadOperators()
    } catch (error) {
      console.error('Failed to assign operator:', error)
      alert('Failed to assign operator')
    }
  }

  // Handle remove operator
  const handleRemoveOperator = async (craftsmanId: number) => {
    if (!id) return

    if (!confirm('Are you sure you want to remove this operator?')) return

    try {
      await equipmentService.removeOperator(parseInt(id), craftsmanId)
      loadOperators()
    } catch (error) {
      console.error('Failed to remove operator:', error)
      alert('Failed to remove operator')
    }
  }

  // Handle delete equipment
  const handleDelete = async () => {
    if (!id || !equipment) return

    if (!confirm(`Are you sure you want to delete ${equipment.name}?`)) return

    try {
      await equipmentService.delete(parseInt(id))
      navigate('/equipment')
    } catch (error) {
      console.error('Failed to delete equipment:', error)
      alert('Failed to delete equipment')
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading equipment details...</p>
        </div>
      </div>
    )
  }

  if (!equipment) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="text-center">
          <p className="text-gray-600">Equipment not found</p>
          <button
            onClick={() => navigate('/equipment')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Back to Equipment List
          </button>
        </div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    const colors = {
      OPERATIONAL: 'bg-green-100 text-green-800',
      MAINTENANCE: 'bg-yellow-100 text-yellow-800',
      BREAKDOWN: 'bg-red-100 text-red-800',
      RETIRED: 'bg-gray-100 text-gray-800',
    }
    return colors[status as keyof typeof colors] || colors.OPERATIONAL
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/equipment')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Equipment
        </button>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 h-16 w-16 bg-blue-100 rounded-lg flex items-center justify-center">
                <Wrench className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{equipment.name}</h1>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                  <span>ID: {equipment.equipment_id}</span>
                  {equipment.category && <span>• {equipment.category}</span>}
                  {equipment.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {equipment.location}
                    </span>
                  )}
                </div>
                <div className="mt-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(equipment.status)}`}>
                    {equipment.status}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => navigate(`/equipment/${id}/edit`)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={handleDelete}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-lg hover:bg-red-50"
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
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: FileText },
              { id: 'operators', label: 'Operators', icon: Users },
              { id: 'maintenance', label: 'Maintenance', icon: Wrench },
              { id: 'history', label: 'History', icon: Activity },
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
      <div className="bg-white rounded-lg shadow-sm p-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Basic Information</h3>
              <dl className="space-y-3">
                {[
                  { label: 'Manufacturer', value: equipment.manufacturer },
                  { label: 'Model', value: equipment.model },
                  { label: 'Serial Number', value: equipment.serial_number },
                  { label: 'Purchase Date', value: equipment.purchase_date },
                  { label: 'Warranty Expiry', value: equipment.warranty_expiry },
                ].map((item) => (
                  <div key={item.label} className="flex justify-between">
                    <dt className="text-sm font-medium text-gray-600">{item.label}:</dt>
                    <dd className="text-sm text-gray-900">{item.value || '-'}</dd>
                  </div>
                ))}
              </dl>
            </div>

            {equipment.specifications && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Specifications</h3>
                <p className="text-sm text-gray-700">{equipment.specifications}</p>
              </div>
            )}

            {equipment.notes && (
              <div className="md:col-span-2">
                <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Notes</h3>
                <p className="text-sm text-gray-700">{equipment.notes}</p>
              </div>
            )}
          </div>
        )}

        {/* Operators Tab */}
        {activeTab === 'operators' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Assigned Operators</h3>
              <button
                onClick={() => {
                  setIsAddingOperator(true)
                  loadAvailableCraftsmen()
                }}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              >
                <Plus className="w-4 h-4" />
                Assign Operator
              </button>
            </div>

            {/* Add Operator Form */}
            {isAddingOperator && (
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <select
                    value={selectedCraftsmanId || ''}
                    onChange={(e) => setSelectedCraftsmanId(parseInt(e.target.value))}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select craftsman...</option>
                    {availableCraftsmen.map((craftsman) => (
                      <option key={craftsman.id} value={craftsman.id}>
                        {craftsman.user.full_name} ({craftsman.employee_id})
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={handleAssignOperator}
                    disabled={!selectedCraftsmanId}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Assign
                  </button>
                  <button
                    onClick={() => {
                      setIsAddingOperator(false)
                      setSelectedCraftsmanId(null)
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Operators List */}
            {operators.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Users className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p>No operators assigned</p>
              </div>
            ) : (
              <div className="space-y-2">
                {operators.map((operator) => (
                  <div
                    key={operator.craftsman_id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{operator.craftsman_name}</p>
                      <p className="text-sm text-gray-500">ID: {operator.employee_id}</p>
                    </div>
                    <button
                      onClick={() => handleRemoveOperator(operator.craftsman_id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Maintenance Tab */}
        {activeTab === 'maintenance' && (
          <div className="text-center py-8 text-gray-500">
            <Wrench className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>Maintenance history coming soon</p>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="text-center py-8 text-gray-500">
            <Activity className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>Equipment history coming soon</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default EquipmentDetailPage
