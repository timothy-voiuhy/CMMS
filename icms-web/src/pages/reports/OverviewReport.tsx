import { Package, Wrench, TrendingUp, ClipboardCheck, Clock, Users, DollarSign } from 'lucide-react'
import type {
  EquipmentSummary,
  MaintenanceSummary,
  InventorySummary,
  ProductionSummary,
  QualitySummary,
  WorkOrdersSummary,
  PersonnelSummary,
  FinancialSummary
} from '../../services/reports.service'

interface OverviewReportProps {
  equipmentSummary: EquipmentSummary | null
  maintenanceSummary: MaintenanceSummary | null
  inventorySummary: InventorySummary | null
  productionSummary: ProductionSummary | null
  qualitySummary: QualitySummary | null
  workOrdersSummary: WorkOrdersSummary | null
  personnelSummary: PersonnelSummary | null
  financialSummary: FinancialSummary | null
}

const OverviewReport = ({
  equipmentSummary,
  maintenanceSummary,
  inventorySummary,
  productionSummary,
  qualitySummary,
  workOrdersSummary,
  personnelSummary,
  financialSummary
}: OverviewReportProps) => {
  return (
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
  )
}

export default OverviewReport
