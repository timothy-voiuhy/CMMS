import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Layouts
import MainLayout from './layouts/MainLayout'
import AuthLayout from './layouts/AuthLayout'

// Pages
import LoginPage from './pages/auth/LoginPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import EquipmentListPage from './pages/equipment/EquipmentListPage'
import EquipmentDetailPage from './pages/equipment/EquipmentDetailPage'
import EquipmentFormPage from './pages/equipment/EquipmentFormPage'
import CraftsmenListPage from './pages/craftsmen/CraftsmenListPage'
import CraftsmenDetailPage from './pages/craftsmen/CraftsmenDetailPage'
import CraftsmenFormPage from './pages/craftsmen/CraftsmenFormPage'
import InventoryListPage from './pages/inventory/InventoryListPage'
import InventoryDetailPage from './pages/inventory/InventoryDetailPage'
import InventoryFormPage from './pages/inventory/InventoryFormPage'
import InventoryCategoriesPage from './pages/inventory/InventoryCategoriesPage'
import InventoryGridPage from './pages/inventory/InventoryGridPage'
import WorkOrdersListPage from './pages/workOrders/WorkOrdersListPage'
import WorkOrderDetailPage from './pages/workOrders/WorkOrderDetailPage'
import WorkOrderFormPage from './pages/workOrders/WorkOrderFormPage'
import MaintenanceListPage from './pages/maintenance/MaintenanceListPage'
import MaintenanceDetailPage from './pages/maintenance/MaintenanceDetailPage'
import MaintenanceFormPage from './pages/maintenance/MaintenanceFormPage'
import MaintenancePersonnelPage from './pages/maintenance/MaintenancePersonnelPage'
import ProductionLinesPage from './pages/production/ProductionLinesPage'
import ProductionLineFormPage from './pages/production/ProductionLineFormPage'
import ProductionLineDetailPage from './pages/production/ProductionLineDetailPage'
import ProductionOrdersPage from './pages/production/ProductionOrdersPage'
import ProductionOrderFormPage from './pages/production/ProductionOrderFormPage'
import ProductionOrderDetailPage from './pages/production/ProductionOrderDetailPage'
import PackagingPage from './pages/production/PackagingPage'
import PackagingFormPage from './pages/production/PackagingFormPage'
import PackagingDetailPage from './pages/production/PackagingDetailPage'
import QualityPage from './pages/quality/QualityPage'
import ReportsPage from './pages/reports/ReportsPage'
import SettingsPage from './pages/settings/SettingsPage'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Auth Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>

        {/* Protected Routes */}
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          
          {/* Equipment Routes */}
          <Route path="/equipment" element={<EquipmentListPage />} />
          <Route path="/equipment/new" element={<EquipmentFormPage />} />
          <Route path="/equipment/:id/edit" element={<EquipmentFormPage />} />
          <Route path="/equipment/:id" element={<EquipmentDetailPage />} />
          
          {/* Craftsmen Routes */}
          <Route path="/craftsmen" element={<CraftsmenListPage />} />
          <Route path="/craftsmen/new" element={<CraftsmenFormPage />} />
          <Route path="/craftsmen/:id/edit" element={<CraftsmenFormPage />} />
          <Route path="/craftsmen/:id" element={<CraftsmenDetailPage />} />
          
          {/* Inventory Routes */}
          <Route path="/inventory" element={<InventoryListPage />} />
          <Route path="/inventory/grid" element={<InventoryGridPage />} />
          <Route path="/inventory/categories" element={<InventoryCategoriesPage />} />
          <Route path="/inventory/new" element={<InventoryFormPage />} />
          <Route path="/inventory/:id/edit" element={<InventoryFormPage />} />
          <Route path="/inventory/:id" element={<InventoryDetailPage />} />
          
          {/* Maintenance Routes */}
          <Route path="/maintenance" element={<MaintenanceListPage />} />
          <Route path="/maintenance/reports" element={<MaintenanceListPage />} />
          <Route path="/maintenance/reports/new" element={<MaintenanceFormPage />} />
          <Route path="/maintenance/reports/:id/edit" element={<MaintenanceFormPage />} />
          <Route path="/maintenance/reports/:id" element={<MaintenanceDetailPage />} />
          <Route path="/maintenance/new" element={<MaintenanceFormPage />} />
          <Route path="/maintenance/:id/edit" element={<MaintenanceFormPage />} />
          <Route path="/maintenance/:id" element={<MaintenanceDetailPage />} />
          <Route path="/maintenance/work-orders" element={<WorkOrdersListPage />} />
          <Route path="/maintenance/work-orders/new" element={<WorkOrderFormPage />} />
          <Route path="/maintenance/work-orders/:id/edit" element={<WorkOrderFormPage />} />
          <Route path="/maintenance/work-orders/:id" element={<WorkOrderDetailPage />} />
          <Route path="/maintenance/personnel" element={<MaintenancePersonnelPage />} />
          
          {/* Production Routes */}
          <Route path="/production/lines" element={<ProductionLinesPage />} />
          <Route path="/production/lines/new" element={<ProductionLineFormPage />} />
          <Route path="/production/lines/:id/edit" element={<ProductionLineFormPage />} />
          <Route path="/production/lines/:id" element={<ProductionLineDetailPage />} />
          <Route path="/production/orders" element={<ProductionOrdersPage />} />
          <Route path="/production/orders/new" element={<ProductionOrderFormPage />} />
          <Route path="/production/orders/:id/edit" element={<ProductionOrderFormPage />} />
          <Route path="/production/orders/:id" element={<ProductionOrderDetailPage />} />
          <Route path="/production/packaging" element={<PackagingPage />} />
          <Route path="/production/packaging/new" element={<PackagingFormPage />} />
          <Route path="/production/packaging/:id/edit" element={<PackagingFormPage />} />
          <Route path="/production/packaging/:id" element={<PackagingDetailPage />} />
          
          {/* Quality Routes */}
          <Route path="/quality" element={<QualityPage />} />
          
          {/* Reports Routes */}
          <Route path="/reports" element={<ReportsPage />} />
          
          {/* Settings Routes */}
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
