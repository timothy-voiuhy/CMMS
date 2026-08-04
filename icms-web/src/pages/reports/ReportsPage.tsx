import { useState, useEffect } from 'react'
import {
  BarChart3,
  TrendingUp,
  Package,
  Wrench,
  ClipboardCheck,
  Users,
  DollarSign,
  Download,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { reportsService } from '../../services/reports.service'
import type {
  EquipmentSummary,
  MaintenanceSummary,
  InventorySummary,
  ProductionSummary,
  QualitySummary,
  WorkOrdersSummary,
  PersonnelSummary,
  FinancialSummary,
  LowStockReport
} from '../../services/reports.service'

type ReportCategory =
  | 'overview'
  | 'equipment'
  | 'maintenance'
  | 'inventory'
  | 'production'
  | 'quality'
  | 'work-orders'
  | 'personnel'
  | 'financial'

const ReportsPage = () => {
  const [activeCategory, setActiveCategory] = useState<ReportCategory>('overview')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })

  // Report data states
  const [equipmentSummary, setEquipmentSummary] = useState<EquipmentSummary | null>(null)
  const [maintenanceSummary, setMaintenanceSummary] = useState<MaintenanceSummary | null>(null)
  const [inventorySummary, setInventorySummary] = useState<InventorySummary | null>(null)
  const [productionSummary, setProductionSummary] = useState<ProductionSummary | null>(null)
  const [qualitySummary, setQualitySummary] = useState<QualitySummary | null>(null)
  const [workOrdersSummary, setWorkOrdersSummary] = useState<WorkOrdersSummary | null>(null)
  const [personnelSummary, setPersonnelSummary] = useState<PersonnelSummary | null>(null)
  const [financialSummary, setFinancialSummary] = useState<FinancialSummary | null>(null)
  const [lowStockReport, setLowStockReport] = useState<LowStockReport | null>(null)

  useEffect(() => {
    loadReports()
  }, [activeCategory, dateRange])

  const loadReports = async () => {
    setLoading(true)
    setError(null)

    try {
      switch (activeCategory) {
        case 'overview':
          await loadOverviewReports()
          break
        case 'equipment':
          const eqData = await reportsService.getEquipmentSummary()
          setEquipmentSummary(eqData)
          break
        case 'maintenance':
          const maintData = await reportsService.getMaintenanceSummary(dateRange.start, dateRange.end)
          setMaintenanceSummary(maintData)
          break
        case 'inventory':
          const invData = await reportsService.getInventorySummary()
          const lowStockData = await reportsService.getLowStockReport()
          setInventorySummary(invData)
          setLowStockReport(lowStockData)
          break
        case 'production':
          const prodData = await reportsService.getProductionSummary(dateRange.start, dateRange.end)
          setProductionSummary(prodData)
          break
        case 'quality':
          const qualData = await reportsService.getQualitySummary(dateRange.start, dateRange.end)
          setQualitySummary(qualData)
          break
        case 'work-orders':
          const woData = await reportsService.getWorkOrdersSummary(dateRange.start, dateRange.end)
          setWorkOrdersSummary(woData)
          break
        case 'personnel':
          const persData = await reportsService.getPersonnelSummary()
          setPersonnelSummary(persData)
          break
        case 'financial':
          const finData = await reportsService.getFinancialSummary(dateRange.start, dateRange.end)
          setFinancialSummary(finData)
          break
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load reports')
    } finally {
      setLoading(false)
    }
  }

  const loadOverviewReports = async () => {
    const [eq, maint, inv, prod, qual, wo, pers, fin] = await Promise.all([
      reportsService.getEquipmentSummary(),
      reportsService.getMaintenanceSummary(dateRange.start, dateRange.end),
      reportsService.getInventorySummary(),
      reportsService.getProductionSummary(dateRange.start, dateRange.end),
      reportsService.getQualitySummary(dateRange.start, dateRange.end),
      reportsService.getWorkOrdersSummary(dateRange.start, dateRange.end),
      reportsService.getPersonnelSummary(),
      reportsService.getFinancialSummary(dateRange.start, dateRange.end)
    ])

    setEquipmentSummary(eq)
    setMaintenanceSummary(maint)
    setInventorySummary(inv)
    setProductionSummary(prod)
    setQualitySummary(qual)
    setWorkOrdersSummary(wo)
    setPersonnelSummary(pers)
    setFinancialSummary(fin)
  }

  const categories = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'equipment', label: 'Equipment', icon: Package },
    { id: 'maintenance', label: 'Maintenance', icon: Wrench },
    { id: 'inventory', label: 'Inventory', icon: Package },
    { id: 'production', label: 'Production', icon: TrendingUp },
    { id: 'quality', label: 'Quality', icon: ClipboardCheck },
    { id: 'work-orders', label: 'Work Orders', icon: Clock },
    { id: 'personnel', label: 'Personnel', icon: Users },
    { id: 'financial', label: 'Financial', icon: DollarSign }
  ]

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Reports & Analytics</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Comprehensive reports across all modules
              </p>
            </div>
          </div>

          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-4 py-2 text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30"
          >
            <Download className="w-4 h-4" />
            Export Report
          </button>
        </div>

        {/* Date Range Filter */}
        <div className="flex items-center gap-4 bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-4">
          <Calendar className="w-5 h-5 text-gray-400 dark:text-gray-500" />
          <div className="flex items-center gap-3">
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Start Date</label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">End Date</label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-800 dark:text-red-300">
            {error}
          </div>
        )}
      </div>

      {/* Category Tabs */}
      <div className="mb-6 overflow-x-auto">
        <div className="flex gap-2 min-w-max">
          {categories.map((cat) => {
            const Icon = cat.icon
            return (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id as ReportCategory)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeCategory === cat.id
                    ? 'bg-blue-600 dark:bg-blue-500 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                {cat.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading reports...</p>
        </div>
      )}

      {/* Overview Dashboard */}
      {!loading && activeCategory === 'overview' && (
        <div className="space-y-6">
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Equipment Card */}
            {equipmentSummary && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <Package className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                  <span className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                    {equipmentSummary.total_equipment}
                  </span>
                </div>
                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Equipment</h3>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  {equipmentSummary.average_utilization}% avg utilization
                </p>
              </div>
            )}

            {/* Inventory Card */}
            {inventorySummary && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <Package className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                  <span className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                    {inventorySummary.total_items}
                  </span>
                </div>
                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Inventory Items</h3>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  ${inventorySummary.total_value.toLocaleString()} total value
                </p>
              </div>
            )}

            {/* Production Card */}
            {productionSummary && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
                  <span className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                    {productionSummary.total_orders}
                  </span>
                </div>
                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Production Orders</h3>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  {productionSummary.total_quantity_produced.toLocaleString()} units produced
                </p>
              </div>
            )}

            {/* Quality Card */}
            {qualitySummary && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <ClipboardCheck className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
                  <span className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                    {qualitySummary.pass_rate}%
                  </span>
                </div>
                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Quality Pass Rate</h3>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  {qualitySummary.total_inspections} inspections
                </p>
              </div>
            )}
          </div>

          {/* Summary Sections */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Maintenance Summary */}
            {maintenanceSummary && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                  <Wrench className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                  Maintenance Overview
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Maintenance</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">
                      {maintenanceSummary.total_maintenance}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Average Cost</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">
                      ${maintenanceSummary.average_cost.toLocaleString()}
                    </span>
                  </div>
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-sm text-gray-500 dark:text-gray-500 mb-2">By Type:</p>
                    <div className="space-y-1">
                      {maintenanceSummary.by_type.map((item) => (
                        <div key={item.type} className="flex justify-between text-sm">
                          <span className="text-gray-600 dark:text-gray-400 capitalize">{item.type}</span>
                          <span className="text-gray-800 dark:text-gray-100">{item.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Work Orders Summary */}
            {workOrdersSummary && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  Work Orders Overview
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Work Orders</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">
                      {workOrdersSummary.total_work_orders}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Overdue</span>
                    <span className="font-semibold text-red-600 dark:text-red-400">
                      {workOrdersSummary.overdue}
                    </span>
                  </div>
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-sm text-gray-500 dark:text-gray-500 mb-2">By Status:</p>
                    <div className="space-y-1">
                      {workOrdersSummary.by_status.map((item) => (
                        <div key={item.status} className="flex justify-between text-sm">
                          <span className="text-gray-600 dark:text-gray-400 capitalize">{item.status}</span>
                          <span className="text-gray-800 dark:text-gray-100">{item.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Personnel & Financial */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {personnelSummary && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
                  Personnel Summary
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Craftsmen</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">
                      {personnelSummary.total_craftsmen}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Active</span>
                    <span className="font-semibold text-green-600 dark:text-green-400">
                      {personnelSummary.active_craftsmen}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Avg Experience</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">
                      {personnelSummary.average_experience_years} years
                    </span>
                  </div>
                </div>
              </div>
            )}

            {financialSummary && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                  Financial Summary
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Maintenance Cost</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">
                      ${financialSummary.maintenance_cost.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Inventory Value</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">
                      ${financialSummary.inventory_value.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Equipment Reports */}
      {!loading && activeCategory === 'equipment' && equipmentSummary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Equipment</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{equipmentSummary.total_equipment}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Avg Utilization</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{equipmentSummary.average_utilization}%</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Critical Equipment</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{equipmentSummary.critical_equipment}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Status</h3>
              <div className="space-y-3">
                {equipmentSummary.by_status.map((item) => (
                  <div key={item.status} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{item.status}</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Type</h3>
              <div className="space-y-3">
                {equipmentSummary.by_type.map((item) => (
                  <div key={item.type} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{item.type}</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Maintenance Reports */}
      {!loading && activeCategory === 'maintenance' && maintenanceSummary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Maintenance</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{maintenanceSummary.total_maintenance}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Average Cost</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">
                ${maintenanceSummary.average_cost.toLocaleString()}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Date Range</h3>
              <p className="text-sm text-gray-800 dark:text-gray-100">
                {new Date(maintenanceSummary.start_date).toLocaleDateString()} - 
                {new Date(maintenanceSummary.end_date).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Type</h3>
              <div className="space-y-3">
                {maintenanceSummary.by_type.map((item) => (
                  <div key={item.type} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{item.type}</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Priority</h3>
              <div className="space-y-3">
                {maintenanceSummary.by_priority.map((item) => (
                  <div key={item.priority} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{item.priority}</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Inventory Reports */}
      {!loading && activeCategory === 'inventory' && inventorySummary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Items</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{inventorySummary.total_items}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Value</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">
                ${inventorySummary.total_value.toLocaleString()}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Low Stock</h3>
              <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
                {inventorySummary.low_stock_items}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Out of Stock</h3>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">
                {inventorySummary.out_of_stock}
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Category</h3>
            <div className="space-y-3">
              {inventorySummary.by_category.map((item) => (
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
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Item</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Category</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Quantity</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Reorder Level</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Shortage</th>
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
      )}

      {/* Production Reports */}
      {!loading && activeCategory === 'production' && productionSummary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Orders</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{productionSummary.total_orders}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Units Produced</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">
                {productionSummary.total_quantity_produced.toLocaleString()}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Active Lines</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{productionSummary.active_lines}</p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Status</h3>
            <div className="space-y-3">
              {productionSummary.by_status.map((item) => (
                <div key={item.status} className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400 capitalize">{item.status}</span>
                  <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Quality Reports */}
      {!loading && activeCategory === 'quality' && qualitySummary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Inspections</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{qualitySummary.total_inspections}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Pass Rate</h3>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">{qualitySummary.pass_rate}%</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total NCRs</h3>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">{qualitySummary.total_ncrs}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Period</h3>
              <p className="text-sm text-gray-800 dark:text-gray-100">
                {new Date(qualitySummary.start_date).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Inspection Results</h3>
              <div className="space-y-3">
                {qualitySummary.by_result.map((item) => (
                  <div key={item.result} className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      {item.result === 'passed' && <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />}
                      {item.result === 'failed' && <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400" />}
                      <span className="text-gray-600 dark:text-gray-400 capitalize">{item.result}</span>
                    </div>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">NCRs by Severity</h3>
              <div className="space-y-3">
                {qualitySummary.ncrs_by_severity.map((item) => (
                  <div key={item.severity} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{item.severity}</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Work Orders Reports */}
      {!loading && activeCategory === 'work-orders' && workOrdersSummary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Work Orders</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">
                {workOrdersSummary.total_work_orders}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Overdue</h3>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">{workOrdersSummary.overdue}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Period</h3>
              <p className="text-sm text-gray-800 dark:text-gray-100">
                {new Date(workOrdersSummary.start_date).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Status</h3>
              <div className="space-y-3">
                {workOrdersSummary.by_status.map((item) => (
                  <div key={item.status} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{item.status}</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Priority</h3>
              <div className="space-y-3">
                {workOrdersSummary.by_priority.map((item) => (
                  <div key={item.priority} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{item.priority}</span>
                    <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Personnel Reports */}
      {!loading && activeCategory === 'personnel' && personnelSummary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Craftsmen</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{personnelSummary.total_craftsmen}</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Active Craftsmen</h3>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                {personnelSummary.active_craftsmen}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Avg Experience</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">
                {personnelSummary.average_experience_years} yrs
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Specialization</h3>
            <div className="space-y-3">
              {personnelSummary.by_specialization.map((item) => (
                <div key={item.specialization} className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400 capitalize">{item.specialization}</span>
                  <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Financial Reports */}
      {!loading && activeCategory === 'financial' && financialSummary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Maintenance Cost</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">
                ${financialSummary.maintenance_cost.toLocaleString()}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Inventory Value</h3>
              <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">
                ${financialSummary.inventory_value.toLocaleString()}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Period</h3>
              <p className="text-sm text-gray-800 dark:text-gray-100">
                {new Date(financialSummary.start_date).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Inventory Transactions</h3>
            <div className="space-y-3">
              {financialSummary.inventory_transactions.map((item) => (
                <div key={item.type} className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400 capitalize">{item.type}</span>
                  <span className="font-semibold text-gray-800 dark:text-gray-100">
                    ${item.value.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportsPage
