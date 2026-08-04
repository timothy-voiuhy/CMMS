import type { EquipmentSummary } from '../../services/reports.service'

interface EquipmentReportProps {
  summary: EquipmentSummary
}

const EquipmentReport = ({ summary }: EquipmentReportProps) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Equipment</h3>
          <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{summary.total_equipment}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Avg Utilization</h3>
          <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{summary.average_utilization}%</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Critical Equipment</h3>
          <p className="text-3xl font-bold text-gray-800 dark:text-gray-100">{summary.critical_equipment}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">By Status</h3>
          <div className="space-y-3">
            {summary.by_status.map((item) => (
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
            {summary.by_type.map((item) => (
              <div key={item.type} className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400 capitalize">{item.type}</span>
                <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default EquipmentReport
