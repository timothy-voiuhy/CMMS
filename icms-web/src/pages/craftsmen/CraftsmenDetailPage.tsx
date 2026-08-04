import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  Calendar,
  Briefcase,
  Award,
  Wrench,
  ClipboardList,
  TrendingUp,
} from 'lucide-react'
import { craftsmanService, type CraftsmanWithUser } from '../../services/craftsman.service'

const CraftsmenDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [craftsman, setCraftsman] = useState<CraftsmanWithUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState({
    totalWorkOrders: 0,
    completedWorkOrders: 0,
    pendingWorkOrders: 0,
    averageCompletionTime: 0,
  })
  const [equipment, setEquipment] = useState<any[]>([])
  const [workOrders, setWorkOrders] = useState<any[]>([])

  useEffect(() => {
    if (id && id !== 'new') {
      loadCraftsmanDetails()
    }
  }, [id])

  const loadCraftsmanDetails = async () => {
    if (!id || id === 'new') return

    try {
      setIsLoading(true)
      const craftsmanId = parseInt(id)

      if (isNaN(craftsmanId)) {
        navigate('/craftsmen')
        return
      }

      // Load craftsman details
      const craftsmanData = await craftsmanService.getById(craftsmanId)
      setCraftsman(craftsmanData)

      // Load statistics
      const statsData = await craftsmanService.getStatistics(craftsmanId)
      setStats(statsData)

      // Load equipment
      const equipmentData = await craftsmanService.getOperatedEquipment(craftsmanId)
      setEquipment(equipmentData)

      // Load work orders
      const workOrdersData = await craftsmanService.getWorkOrders(craftsmanId)
      setWorkOrders(workOrdersData)
    } catch (error) {
      console.error('Failed to load craftsman details:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    )
  }

  if (!craftsman) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-gray-500 dark:text-gray-400">Craftsman not found</p>
          <button
            onClick={() => navigate('/craftsmen')}
            className="mt-4 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-500"
          >
            Back to Craftsmen List
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
          onClick={() => navigate('/craftsmen')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Craftsmen
        </button>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
              <span className="text-blue-600 dark:text-blue-400 font-bold text-2xl">
                {craftsman.full_name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{craftsman.full_name}</h1>
              <p className="text-gray-600 dark:text-gray-400">{craftsman.position || 'Craftsman'}</p>
            </div>
          </div>
          <button
            onClick={() => navigate(`/craftsmen/${id}/edit`)}
            className="px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
          >
            Edit Profile
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Personal Info */}
        <div className="lg:col-span-1 space-y-6">
          {/* Basic Info Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Personal Information</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <User className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Employee ID</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{craftsman.employee_id}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{craftsman.email}</p>
                </div>
              </div>
              {craftsman.phone && (
                <div className="flex items-start gap-3">
                  <Phone className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Phone</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{craftsman.phone}</p>
                  </div>
                </div>
              )}
              <div className="flex items-start gap-3">
                <Briefcase className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Department</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {craftsman.department || 'N/A'}
                  </p>
                </div>
              </div>
              {craftsman.hire_date && (
                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Hire Date</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {new Date(craftsman.hire_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              )}
              {craftsman.certification_level && (
                <div className="flex items-start gap-3">
                  <Award className="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Certification Level</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {craftsman.certification_level}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Skills Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {craftsman.skills && craftsman.skills.length > 0 ? (
                craftsman.skills.map((skill) => (
                  <span
                    key={skill.id}
                    className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 rounded-full text-sm"
                  >
                    {skill.name}
                  </span>
                ))
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">No skills assigned</p>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Stats and Activity */}
        <div className="lg:col-span-2 space-y-6">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Work Orders</p>
                  <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{stats.totalWorkOrders}</p>
                </div>
                <ClipboardList className="w-8 h-8 text-blue-500 dark:text-blue-400" />
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.completedWorkOrders}</p>
                </div>
                <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                  <span className="text-green-600 dark:text-green-400 font-bold">✓</span>
                </div>
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
                  <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{stats.pendingWorkOrders}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-orange-500 dark:text-orange-400" />
              </div>
            </div>
          </div>

          {/* Equipment Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Wrench className="w-5 h-5" />
              Operated Equipment
            </h2>
            {equipment.length > 0 ? (
              <div className="space-y-3">
                {equipment.map((eq) => (
                  <div
                    key={eq.id}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600"
                  >
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100">{eq.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {eq.equipment_id} • {eq.category}
                      </p>
                    </div>
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        eq.status === 'OPERATIONAL'
                          ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                          : eq.status === 'MAINTENANCE'
                          ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400'
                          : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400'
                      }`}
                    >
                      {eq.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">No equipment assigned</p>
            )}
          </div>

          {/* Work Orders Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
              <ClipboardList className="w-5 h-5" />
              Recent Work Orders
            </h2>
            {workOrders.length > 0 ? (
              <div className="space-y-3">
                {workOrders.slice(0, 5).map((wo) => (
                  <div
                    key={wo.id}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
                    onClick={() => navigate(`/work-orders/${wo.id}`)}
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-gray-100">{wo.title}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">WO-{wo.work_order_number}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          wo.priority === 'HIGH'
                            ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400'
                            : wo.priority === 'MEDIUM'
                            ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400'
                            : 'bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-300'
                        }`}
                      >
                        {wo.priority}
                      </span>
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          wo.status === 'COMPLETED'
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                            : wo.status === 'IN_PROGRESS'
                            ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400'
                            : 'bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-300'
                        }`}
                      >
                        {wo.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">No work orders assigned</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CraftsmenDetailPage
