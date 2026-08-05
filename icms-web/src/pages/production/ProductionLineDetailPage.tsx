import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Edit,
  Trash2,
  Factory,
  MapPin,
  Activity,
  Plus,
  Clock,
  Users,
  Calendar,
  Loader,
  Settings,
  ArrowUp,
  ArrowDown,
  X,
} from 'lucide-react'
import {
  productionLineService,
  shiftService,
  type ProductionLine,
  type Shift,
  type CreateShiftRequest,
  type ProductionLineEquipmentStation,
  type CreateEquipmentStationRequest,
} from '../../services/production.service'
import { equipmentService } from '../../services/equipment.service'
import { craftsmanService, type CraftsmanWithUser } from '../../services/craftsman.service'
import type { Equipment } from '../../types'

const ProductionLineDetailPage: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [line, setLine] = useState<ProductionLine | null>(null)
  const [shifts, setShifts] = useState<Shift[]>([])
  const [equipmentStations, setEquipmentStations] = useState<ProductionLineEquipmentStation[]>([])
  const [availableEquipment, setAvailableEquipment] = useState<Equipment[]>([])
  const [availableCraftsmen, setAvailableCraftsmen] = useState<CraftsmanWithUser[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showShiftModal, setShowShiftModal] = useState(false)
  const [showEquipmentModal, setShowEquipmentModal] = useState(false)
  const [editingStation, setEditingStation] = useState<ProductionLineEquipmentStation | null>(null)
  const [activeTab, setActiveTab] = useState<'equipment' | 'shifts'>('equipment')
  const [shiftFormData, setShiftFormData] = useState<CreateShiftRequest>({
    production_line_id: 0,
    shift_type: 'morning',
    start_time: '',
    end_time: '',
    team_leader_id: undefined,
    operators: [],
    active_days: [1, 2, 3, 4, 5], // Mon-Fri
    is_active: true,
  })
  const [equipmentFormData, setEquipmentFormData] = useState<CreateEquipmentStationRequest>({
    production_line_id: 0,
    equipment_id: 0,
    sequence_order: 1,
    station_name: '',
    operators: [],
    cycle_time_minutes: undefined,
    notes: '',
  })

  useEffect(() => {
    loadData()
    loadResources()
  }, [id])

  const loadData = async () => {
    if (!id || id === 'new') return
    
    try {
      setIsLoading(true)
      const lineId = parseInt(id)
      const [lineData, shiftsData, stationsData] = await Promise.all([
        productionLineService.getById(lineId),
        shiftService.getByLine(lineId),
        productionLineService.getEquipmentStations(lineId),
      ])
      setLine(lineData)
      setShifts(shiftsData)
      setEquipmentStations(stationsData)
      setShiftFormData((prev) => ({ ...prev, production_line_id: lineId }))
      setEquipmentFormData((prev) => ({ ...prev, production_line_id: lineId, sequence_order: stationsData.length + 1 }))
    } catch (error) {
      console.error('Failed to load data:', error)
      alert('Failed to load production line')
      navigate('/production/lines')
    } finally {
      setIsLoading(false)
    }
  }

  const loadResources = async () => {
    try {
      const [equipmentRes, craftsmenRes] = await Promise.all([
        equipmentService.getAll({ limit: 100 }),
        craftsmanService.getAll({ limit: 100 }),
      ])
      setAvailableEquipment(equipmentRes.data)
      setAvailableCraftsmen(craftsmenRes.data)
    } catch (error) {
      console.error('Failed to load resources:', error)
    }
  }

  const handleDelete = async () => {
    if (!line || !confirm(`Are you sure you want to delete ${line.name}?`)) return

    try {
      await productionLineService.delete(line.id)
      navigate('/production/lines')
    } catch (error) {
      console.error('Failed to delete production line:', error)
      alert('Failed to delete production line')
    }
  }

  // Equipment Station Handlers
  const handleAddEquipmentStation = async () => {
    if (!equipmentFormData.equipment_id) {
      alert('Please select equipment')
      return
    }

    try {
      if (editingStation) {
        // Update existing station
        await productionLineService.updateEquipmentStation(editingStation.id, {
          sequence_order: equipmentFormData.sequence_order,
          station_name: equipmentFormData.station_name || undefined,
          operators: equipmentFormData.operators,
          cycle_time_minutes: equipmentFormData.cycle_time_minutes,
          notes: equipmentFormData.notes || undefined,
        })
      } else {
        // Create new station
        await productionLineService.addEquipmentStation(parseInt(id!), equipmentFormData)
      }
      
      setShowEquipmentModal(false)
      setEditingStation(null)
      loadData()
      // Reset form
      setEquipmentFormData({
        production_line_id: parseInt(id!),
        equipment_id: 0,
        sequence_order: equipmentStations.length + 2,
        station_name: '',
        operators: [],
        cycle_time_minutes: undefined,
        notes: '',
      })
    } catch (error) {
      console.error('Failed to save equipment station:', error)
      alert('Failed to save equipment station')
    }
  }

  const handleEditStation = (station: ProductionLineEquipmentStation) => {
    setEditingStation(station)
    setEquipmentFormData({
      production_line_id: station.production_line_id,
      equipment_id: station.equipment_id,
      sequence_order: station.sequence_order,
      station_name: station.station_name || '',
      operators: station.operators || [],
      cycle_time_minutes: station.cycle_time_minutes,
      notes: station.notes || '',
    })
    setShowEquipmentModal(true)
  }

  const handleCancelEdit = () => {
    setEditingStation(null)
    setShowEquipmentModal(false)
    setEquipmentFormData({
      production_line_id: parseInt(id!),
      equipment_id: 0,
      sequence_order: equipmentStations.length + 1,
      station_name: '',
      operators: [],
      cycle_time_minutes: undefined,
      notes: '',
    })
  }

  const handleDeleteEquipmentStation = async (stationId: number) => {
    if (!confirm('Are you sure you want to remove this equipment from the line?')) return

    try {
      await productionLineService.deleteEquipmentStation(stationId)
      loadData()
    } catch (error) {
      console.error('Failed to delete equipment station:', error)
      alert('Failed to delete equipment station')
    }
  }

  const handleMoveStation = async (stationId: number, direction: 'up' | 'down') => {
    const currentIndex = equipmentStations.findIndex((s) => s.id === stationId)
    if (currentIndex === -1) return
    
    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1
    if (newIndex < 0 || newIndex >= equipmentStations.length) return

    const reordered = [...equipmentStations]
    const [moved] = reordered.splice(currentIndex, 1)
    reordered.splice(newIndex, 0, moved)

    const stationOrders = reordered.map((station, index) => ({
      id: station.id,
      sequence_order: index + 1,
    }))

    try {
      // Optimistically update UI first
      setEquipmentStations(reordered.map((station, index) => ({
        ...station,
        sequence_order: index + 1
      })))
      
      // Then update backend
      await productionLineService.reorderEquipmentStations(parseInt(id!), stationOrders)
      
      // Reload to ensure consistency
      const lineId = parseInt(id!)
      const stationsData = await productionLineService.getEquipmentStations(lineId)
      setEquipmentStations(stationsData)
    } catch (error) {
      console.error('Failed to reorder stations:', error)
      alert('Failed to reorder stations')
      // Reload on error to restore correct order
      loadData()
    }
  }

  const toggleOperator = (craftsmanId: number) => {
    setEquipmentFormData((prev) => {
      const operators = prev.operators || []
      if (operators.includes(craftsmanId)) {
        return { ...prev, operators: operators.filter((id) => id !== craftsmanId) }
      } else {
        return { ...prev, operators: [...operators, craftsmanId] }
      }
    })
  }

  const getEquipmentName = (equipmentId: number) => {
    const equipment = availableEquipment.find((e) => e.id === equipmentId)
    return equipment ? `${equipment.name} (${equipment.equipment_id})` : 'Unknown Equipment'
  }

  const getCraftsmanName = (craftsmanId: number) => {
    const craftsman = availableCraftsmen.find((c) => c.id === craftsmanId)
    return craftsman ? craftsman.user?.full_name ?? craftsman.full_name : 'Unknown'
  }

  const getStatusBadgeColor = (status?: string) => {
    const colors = {
      operational: 'bg-green-100 text-green-800',
      maintenance: 'bg-yellow-100 text-yellow-800',
      out_of_service: 'bg-red-100 text-red-800',
      idle: 'bg-gray-100 text-gray-800',
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const handleCreateShift = async () => {
    try {
      await shiftService.create(shiftFormData)
      setShowShiftModal(false)
      loadData()
      // Reset form
      setShiftFormData({
        production_line_id: parseInt(id!),
        shift_type: 'morning',
        start_time: '',
        end_time: '',
        team_leader_id: undefined,
        operators: [],
        active_days: [1, 2, 3, 4, 5],
        is_active: true,
      })
    } catch (error) {
      console.error('Failed to create shift:', error)
      alert('Failed to create shift')
    }
  }

  const handleDeleteShift = async (shiftId: number) => {
    if (!confirm('Are you sure you want to delete this shift?')) return

    try {
      await shiftService.delete(shiftId)
      loadData()
    } catch (error) {
      console.error('Failed to delete shift:', error)
      alert('Failed to delete shift')
    }
  }

  const getStatusColor = (status: string) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      idle: 'bg-gray-100 text-gray-800',
      maintenance: 'bg-yellow-100 text-yellow-800',
      offline: 'bg-red-100 text-red-800',
    }
    return colors[status as keyof typeof colors] || colors.idle
  }

  const formatShiftType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  const getDayName = (day: number) => {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[day]
  }

  if (isLoading || !line) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-400" />
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/production/lines')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Production Lines
        </button>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{line.name}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">{line.line_code}</p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center sm:gap-3">
            <button
              onClick={() => navigate(`/production/lines/${line.id}/edit`)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              <Edit className="w-4 h-4" />
              Edit
            </button>
            <button
              onClick={handleDelete}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-red-600 dark:bg-red-500 rounded-lg hover:bg-red-700 dark:hover:bg-red-600"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Line Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 mb-4 sm:mb-6">
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Line Information</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mt-1 ${getStatusColor(line.status)}`}>
                  {formatShiftType(line.status)}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Capacity</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-1">
                  {line.capacity_per_hour ? `${line.capacity_per_hour} ${line.capacity_unit || 'units'}/hr` : 'Not set'}
                </p>
              </div>
            </div>
            {line.description && (
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Description</p>
                <p className="text-sm text-gray-900 dark:text-gray-100 mt-1">{line.description}</p>
              </div>
            )}
            {line.location && (
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  Location
                </p>
                <p className="text-sm text-gray-900 dark:text-gray-100 mt-1">
                  {line.location}
                  {line.floor && ` - Floor ${line.floor}`}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Quick Stats</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <Factory className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Shifts</p>
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{shifts.length}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Active Shifts</p>
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {shifts.filter((s) => s.is_active).length}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabbed Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <div className="flex">
            <button
              onClick={() => setActiveTab('equipment')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'equipment'
                  ? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Equipment Configuration
              </div>
            </button>
            <button
              onClick={() => setActiveTab('shifts')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'shifts'
                  ? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Shifts
              </div>
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-4 sm:p-6">
          {activeTab === 'equipment' && (
            <div>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Production Line Equipment</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Configure equipment stations and assign operators in the order products flow through
                  </p>
                </div>
                <button
                  onClick={() => setShowEquipmentModal(true)}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
                >
                  <Plus className="w-4 h-4" />
                  Add Equipment
                </button>
              </div>

              {equipmentStations.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <Factory className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
                  <p className="text-gray-600 dark:text-gray-300 font-medium">No equipment configured</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Add equipment stations to define your production flow</p>
                </div>
              ) : (
                <div>
                  {/* Visual Flow Diagram */}
                  <div className="mb-6 bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20 rounded-lg p-6">
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4 flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      Production Flow Visualization
                    </h3>
                    <div className="flex items-center gap-2 overflow-x-auto pb-4">
                      {equipmentStations.map((station, index) => (
                        <React.Fragment key={station.id}>
                          {/* Station Card */}
                          <div className="flex-shrink-0 bg-white dark:bg-gray-700 rounded-lg shadow-sm border-2 border-blue-200 dark:border-blue-700 p-3 w-48">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="w-6 h-6 bg-blue-600 dark:bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                                <span className="text-xs font-bold text-white">{station.sequence_order}</span>
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-xs font-semibold text-gray-900 dark:text-gray-100 truncate">
                                  {station.station_name || station.equipment?.name}
                                </p>
                              </div>
                            </div>
                            {station.equipment && (
                              <div className="mb-2">
                                <p className="text-xs text-gray-600 dark:text-gray-400 truncate">{station.equipment.name}</p>
                                {station.equipment.status && (
                                  <span className={`inline-block text-xs px-2 py-0.5 rounded-full mt-1 ${getStatusBadgeColor(station.equipment.status)}`}>
                                    {station.equipment.status}
                                  </span>
                                )}
                              </div>
                            )}
                            {station.cycle_time_minutes && (
                              <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-1">
                                <Clock className="w-3 h-3" />
                                {station.cycle_time_minutes} min
                              </div>
                            )}
                            {station.operators_data && station.operators_data.length > 0 && (
                              <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                                <Users className="w-3 h-3" />
                                {station.operators_data.length} operator(s)
                              </div>
                            )}
                          </div>
                          
                          {/* Arrow */}
                          {index < equipmentStations.length - 1 && (
                            <div className="flex-shrink-0 text-blue-400 dark:text-blue-500">
                              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                              </svg>
                            </div>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>

                  {/* Detailed Station List */}
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Station Details</h3>
                  <div className="space-y-3">
                    {equipmentStations.map((station, index) => (
                      <div
                        key={station.id}
                        className="border-2 border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-600 transition-colors bg-white dark:bg-gray-700"
                      >
                        <div className="flex items-start gap-4">
                          {/* Sequence Order Controls */}
                          <div className="flex flex-col gap-1">
                            <button
                              onClick={() => handleMoveStation(station.id, 'up')}
                              disabled={index === 0}
                              className="p-1 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-30 disabled:cursor-not-allowed"
                              title="Move up"
                            >
                              <ArrowUp className="w-4 h-4" />
                            </button>
                            <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                              <span className="text-sm font-bold text-blue-600 dark:text-blue-400">{station.sequence_order}</span>
                            </div>
                            <button
                              onClick={() => handleMoveStation(station.id, 'down')}
                              disabled={index === equipmentStations.length - 1}
                              className="p-1 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-30 disabled:cursor-not-allowed"
                              title="Move down"
                            >
                              <ArrowDown className="w-4 h-4" />
                            </button>
                          </div>

                          {/* Station Details */}
                          <div className="flex-1">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
                                  {station.station_name || station.equipment?.name || getEquipmentName(station.equipment_id)}
                                </h3>
                                {station.station_name && station.equipment && (
                                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    Equipment: {station.equipment.name} ({station.equipment.equipment_id})
                                  </p>
                                )}
                                {station.equipment?.location && (
                                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-1">
                                    <MapPin className="w-3 h-3" />
                                    {station.equipment.location}
                                  </p>
                                )}
                              </div>
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleEditStation(station)}
                                  className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 p-2 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                                  title="Edit station"
                                >
                                  <Edit className="w-5 h-5" />
                                </button>
                                <button
                                  onClick={() => handleDeleteEquipmentStation(station.id)}
                                  className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 p-2 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                                  title="Remove from line"
                                >
                                  <X className="w-5 h-5" />
                                </button>
                              </div>
                            </div>

                            {/* Station Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                              {station.equipment?.status && (
                                <div>
                                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Equipment Status</p>
                                  <span className={`inline-block text-xs px-2 py-1 rounded-full font-medium ${getStatusBadgeColor(station.equipment.status)}`}>
                                    {station.equipment.status.replace('_', ' ').toUpperCase()}
                                  </span>
                                </div>
                              )}
                              {station.cycle_time_minutes && (
                                <div>
                                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Cycle Time</p>
                                  <div className="flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                                    <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                    {station.cycle_time_minutes} minutes
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Operators */}
                            {station.operators_data && station.operators_data.length > 0 && (
                              <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-3">
                                <div className="flex items-center gap-2 mb-2">
                                  <Users className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    Assigned Operators ({station.operators_data.length})
                                  </p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                  {station.operators_data.map((operator) => (
                                    <div
                                      key={operator.id}
                                      className="bg-white dark:bg-gray-700 px-3 py-2 rounded-lg border border-blue-200 dark:border-blue-700"
                                    >
                                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                        {operator.full_name || 'Unknown'}
                                      </p>
                                      <p className="text-xs text-gray-600 dark:text-gray-400">{operator.employee_id || 'N/A'}</p>
                                      {operator.position && (
                                        <p className="text-xs text-gray-500 dark:text-gray-400">{operator.position}</p>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Notes */}
                            {station.notes && (
                              <div className="mt-3 bg-yellow-50 dark:bg-yellow-900/30 border-l-4 border-yellow-400 dark:border-yellow-500 p-3">
                                <p className="text-xs font-medium text-yellow-800 dark:text-yellow-400 mb-1">Station Notes</p>
                                <p className="text-sm text-yellow-900 dark:text-yellow-300">{station.notes}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'shifts' && (
            <div>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Shifts</h2>
                <button
                  onClick={() => setShowShiftModal(true)}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
                >
                  <Plus className="w-4 h-4" />
                  Add Shift
                </button>
              </div>

              {shifts.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <Clock className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
                  <p className="text-gray-600 dark:text-gray-300 font-medium">No shifts configured</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Add shifts to schedule production operations</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {shifts.map((shift) => (
                    <div key={shift.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-700">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-medium text-gray-900 dark:text-gray-100">{formatShiftType(shift.shift_type)} Shift</h3>
                            <span className={`px-2 py-1 text-xs rounded-full ${shift.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-400'}`}>
                              {shift.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                              <Clock className="w-4 h-4" />
                              {shift.start_time} - {shift.end_time}
                            </div>
                            {shift.operators && shift.operators.length > 0 && (
                              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                                <Users className="w-4 h-4" />
                                {shift.operators.length} Operators
                              </div>
                            )}
                            {shift.active_days && shift.active_days.length > 0 && (
                              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                                <Calendar className="w-4 h-4" />
                                {shift.active_days.map((d) => getDayName(d - 1).slice(0, 3)).join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteShift(shift.id)}
                          className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 ml-4"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Equipment Station Modal */}
      {showEquipmentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-4 sm:p-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">
                {editingStation ? 'Edit Equipment Station' : 'Add Equipment Station'}
              </h2>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Equipment <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={equipmentFormData.equipment_id}
                      onChange={(e) => setEquipmentFormData({ ...equipmentFormData, equipment_id: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      required
                      disabled={!!editingStation}
                    >
                      <option value={0}>Select Equipment</option>
                      {availableEquipment.map((equipment) => (
                        <option key={equipment.id} value={equipment.id}>
                          {equipment.name} ({equipment.equipment_id})
                        </option>
                      ))}
                    </select>
                    {editingStation && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Equipment cannot be changed after creation</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Station Name
                    </label>
                    <input
                      type="text"
                      value={equipmentFormData.station_name}
                      onChange={(e) => setEquipmentFormData({ ...equipmentFormData, station_name: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                      placeholder="e.g., Cutting Station, Assembly Station"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Cycle Time (minutes)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={equipmentFormData.cycle_time_minutes || ''}
                      onChange={(e) => setEquipmentFormData({ ...equipmentFormData, cycle_time_minutes: e.target.value ? parseFloat(e.target.value) : undefined })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                      placeholder="Expected cycle time"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Assign Operators
                  </label>
                  <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-3 max-h-48 overflow-y-auto bg-white dark:bg-gray-700">
                    {availableCraftsmen.length === 0 ? (
                      <p className="text-sm text-gray-500 dark:text-gray-400">No craftsmen available</p>
                    ) : (
                      <div className="space-y-2">
                        {availableCraftsmen.map((craftsman) => (
                          <label key={craftsman.id} className="flex items-center gap-2 hover:bg-gray-50 dark:hover:bg-gray-600 p-2 rounded cursor-pointer">
                            <input
                              type="checkbox"
                              checked={equipmentFormData.operators?.includes(craftsman.id)}
                              onChange={() => toggleOperator(craftsman.id)}
                              className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-900 dark:text-gray-100">
                              {craftsman.user?.full_name || 'Unknown'} ({craftsman.employee_id || 'N/A'})
                            </span>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Notes
                  </label>
                  <textarea
                    value={equipmentFormData.notes}
                    onChange={(e) => setEquipmentFormData({ ...equipmentFormData, notes: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                    rows={3}
                    placeholder="Special instructions or notes for this station..."
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 mt-6">
                <button
                  onClick={handleCancelEdit}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddEquipmentStation}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
                >
                  {editingStation ? 'Update Station' : 'Add Station'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Shift Modal */}
      {showShiftModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-4 sm:p-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Add Shift</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Shift Type <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={shiftFormData.shift_type}
                      onChange={(e) => setShiftFormData({ ...shiftFormData, shift_type: e.target.value as any })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      <option value="morning">Morning</option>
                      <option value="afternoon">Afternoon</option>
                      <option value="night">Night</option>
                      <option value="rotating">Rotating</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
                    <select
                      value={shiftFormData.is_active ? 'active' : 'inactive'}
                      onChange={(e) => setShiftFormData({ ...shiftFormData, is_active: e.target.value === 'active' })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Start Time <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="time"
                      value={shiftFormData.start_time}
                      onChange={(e) => setShiftFormData({ ...shiftFormData, start_time: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      End Time <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="time"
                      value={shiftFormData.end_time}
                      onChange={(e) => setShiftFormData({ ...shiftFormData, end_time: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowShiftModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateShift}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
                >
                  Create Shift
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProductionLineDetailPage
