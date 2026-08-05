import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore, type User as AuthStoreUser } from './store/authStore'
import { useThemeStore } from './store/themeStore'
import { useCompanyStore } from './store/companyStore'
import { PermissionRoute } from './components/auth/PermissionGuard'

// Layouts
import MainLayout from './layouts/MainLayout'
import AuthLayout from './layouts/AuthLayout'

// Pages
import LoginPage from './pages/auth/LoginPage'
import SetupPage from './pages/auth/SetupPage'
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
import InventoryRequisitionsPage from './pages/inventory/InventoryRequisitionsPage'
import InventoryRequisitionFormPage from './pages/inventory/InventoryRequisitionFormPage'
import InventoryRequisitionDetailPage from './pages/inventory/InventoryRequisitionDetailPage'
import WorkOrdersListPage from './pages/workOrders/WorkOrdersListPage'
import WorkOrderDetailPage from './pages/workOrders/WorkOrderDetailPage'
import WorkOrderFormPage from './pages/workOrders/WorkOrderFormPage'
import MaintenanceListPage from './pages/maintenance/MaintenanceListPage'
import MaintenanceDetailPage from './pages/maintenance/MaintenanceDetailPage'
import MaintenanceFormPage from './pages/maintenance/MaintenanceFormPage'
import MaintenancePersonnelPage from './pages/maintenance/MaintenancePersonnelPage'
import MaintenanceCataloguePage from './pages/maintenance/MaintenanceCataloguePage'
import ProductionLinesPage from './pages/production/ProductionLinesPage'
import ProductionLineFormPage from './pages/production/ProductionLineFormPage'
import ProductionLineDetailPage from './pages/production/ProductionLineDetailPage'
import ProductionOrdersPage from './pages/production/ProductionOrdersPage'
import ProductionOrderFormPage from './pages/production/ProductionOrderFormPage'
import ProductionOrderDetailPage from './pages/production/ProductionOrderDetailPage'
import PackagingPage from './pages/production/PackagingPage'
import PackagingFormPage from './pages/production/PackagingFormPage'
import PackagingDetailPage from './pages/production/PackagingDetailPage'
import SalesOrdersPage from './pages/sales/SalesOrdersPage'
import SalesOrderFormPage from './pages/sales/SalesOrderFormPage'
import SalesOrderDetailPage from './pages/sales/SalesOrderDetailPage'
import CustomersPage from './pages/sales/CustomersPage'
import QualityPage from './pages/quality/QualityPage'
import InspectionFormPage from './pages/quality/InspectionFormPage'
import NCRFormPage from './pages/quality/NCRFormPage'
import ReportsPage from './pages/reports/ReportsPage'
import SettingsPage from './pages/settings/SettingsPage'
import ProfilePage from './pages/profile/ProfilePage'
import NotificationsPage from './pages/notifications/NotificationsPage'
import RoleTestingPage from './pages/dev/RoleTestingPage'

import authService from './services/auth.service'

const toAuthStoreRole = (role?: string): AuthStoreUser['role'] => {
  const normalized = (role || 'readonly').toLowerCase()
  const allowedRoles: AuthStoreUser['role'][] = ['admin', 'craftsman', 'inventory', 'production', 'quality', 'manager', 'readonly']
  return allowedRoles.includes(normalized as AuthStoreUser['role'])
    ? normalized as AuthStoreUser['role']
    : 'readonly'
}

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  const { actualTheme } = useThemeStore()
  const { isAuthenticated, updateUser, logout } = useAuthStore()
  const { loadCompany } = useCompanyStore()
  
  // Initialize theme on mount
  useEffect(() => {
    if (actualTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [actualTheme])

  // Sync user profile and permissions from backend on session mount/refresh
  useEffect(() => {
    if (isAuthenticated) {
      authService.getCurrentUser().then((userData) => {
        updateUser({
          id: userData.id.toString(),
          username: userData.username,
          full_name: userData.full_name,
          email: userData.email,
          role: toAuthStoreRole(userData.role),
          is_active: userData.is_active,
          phone: userData.phone,
          created_at: userData.created_at || '',
          updated_at: userData.updated_at || '',
          permissions: userData.permissions || [],
        })
        loadCompany()
      }).catch((err) => {
        console.error('Failed to sync current user session:', err)
        if (err?.response?.status === 401) {
          logout()
        }
      })
    }
  }, [isAuthenticated, loadCompany, logout, updateUser])
  
  return (
    <Router>
      <Routes>
        {/* Auth Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/setup" element={<SetupPage />} />
        </Route>
        <Route path="/dev/role-testing" element={<RoleTestingPage />} />

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
          <Route path="/equipment" element={<PermissionRoute permission="equipment.view"><EquipmentListPage /></PermissionRoute>} />
          <Route path="/equipment/new" element={<PermissionRoute permission="equipment.create"><EquipmentFormPage /></PermissionRoute>} />
          <Route path="/equipment/:id/edit" element={<PermissionRoute permission="equipment.edit"><EquipmentFormPage /></PermissionRoute>} />
          <Route path="/equipment/:id" element={<PermissionRoute permission="equipment.view"><EquipmentDetailPage /></PermissionRoute>} />
          
          {/* Craftsmen Routes */}
          <Route path="/craftsmen" element={<PermissionRoute permission="craftsmen.view"><CraftsmenListPage /></PermissionRoute>} />
          <Route path="/craftsmen/new" element={<PermissionRoute permission="craftsmen.create"><CraftsmenFormPage /></PermissionRoute>} />
          <Route path="/craftsmen/:id/edit" element={<PermissionRoute permission="craftsmen.edit"><CraftsmenFormPage /></PermissionRoute>} />
          <Route path="/craftsmen/:id" element={<PermissionRoute permission="craftsmen.view"><CraftsmenDetailPage /></PermissionRoute>} />
          
          {/* Inventory Routes */}
          <Route path="/inventory" element={<PermissionRoute permission="inventory.view"><InventoryListPage /></PermissionRoute>} />
          <Route path="/inventory/grid" element={<PermissionRoute permission="inventory.view"><InventoryGridPage /></PermissionRoute>} />
          <Route path="/inventory/categories" element={<PermissionRoute permission="inventory.categories"><InventoryCategoriesPage /></PermissionRoute>} />
          <Route path="/inventory/requisitions" element={<PermissionRoute anyOf={["inventory.requisitions.view", "inventory.view"]}><InventoryRequisitionsPage /></PermissionRoute>} />
          <Route path="/inventory/requisitions/new" element={<PermissionRoute anyOf={["inventory.requisitions.create", "inventory.create"]}><InventoryRequisitionFormPage /></PermissionRoute>} />
          <Route path="/inventory/requisitions/:id/edit" element={<PermissionRoute anyOf={["inventory.requisitions.edit", "inventory.edit"]}><InventoryRequisitionFormPage /></PermissionRoute>} />
          <Route path="/inventory/requisitions/:id" element={<PermissionRoute anyOf={["inventory.requisitions.view", "inventory.view"]}><InventoryRequisitionDetailPage /></PermissionRoute>} />
          <Route path="/inventory/new" element={<PermissionRoute permission="inventory.create"><InventoryFormPage /></PermissionRoute>} />
          <Route path="/inventory/:id/edit" element={<PermissionRoute permission="inventory.edit"><InventoryFormPage /></PermissionRoute>} />
          <Route path="/inventory/:id" element={<PermissionRoute permission="inventory.view"><InventoryDetailPage /></PermissionRoute>} />
          
          {/* Maintenance Routes */}
          <Route path="/maintenance" element={<PermissionRoute permission="maintenance.view"><MaintenanceListPage /></PermissionRoute>} />
          <Route path="/maintenance/reports" element={<PermissionRoute permission="maintenance.view"><MaintenanceListPage /></PermissionRoute>} />
          <Route path="/maintenance/reports/new" element={<PermissionRoute permission="maintenance.create"><MaintenanceFormPage /></PermissionRoute>} />
          <Route path="/maintenance/reports/:id/edit" element={<PermissionRoute permission="maintenance.edit"><MaintenanceFormPage /></PermissionRoute>} />
          <Route path="/maintenance/reports/:id" element={<PermissionRoute permission="maintenance.view"><MaintenanceDetailPage /></PermissionRoute>} />
          <Route path="/maintenance/new" element={<PermissionRoute permission="maintenance.create"><MaintenanceFormPage /></PermissionRoute>} />
          <Route path="/maintenance/:id/edit" element={<PermissionRoute permission="maintenance.edit"><MaintenanceFormPage /></PermissionRoute>} />
          <Route path="/maintenance/:id" element={<PermissionRoute permission="maintenance.view"><MaintenanceDetailPage /></PermissionRoute>} />
          <Route path="/maintenance/work-orders" element={<PermissionRoute permission="work_orders.view"><WorkOrdersListPage /></PermissionRoute>} />
          <Route path="/maintenance/work-orders/new" element={<PermissionRoute permission="work_orders.create"><WorkOrderFormPage /></PermissionRoute>} />
          <Route path="/maintenance/work-orders/:id/edit" element={<PermissionRoute permission="work_orders.edit"><WorkOrderFormPage /></PermissionRoute>} />
          <Route path="/maintenance/work-orders/:id" element={<PermissionRoute permission="work_orders.view"><WorkOrderDetailPage /></PermissionRoute>} />
          <Route path="/maintenance/personnel" element={<PermissionRoute permission="craftsmen.view"><MaintenancePersonnelPage /></PermissionRoute>} />
          <Route path="/maintenance/catalogue" element={<PermissionRoute anyOf={["maintenance.catalogue.view", "maintenance.view"]}><MaintenanceCataloguePage /></PermissionRoute>} />
          
          {/* Production Routes */}
          <Route path="/production/lines" element={<PermissionRoute permission="production.view"><ProductionLinesPage /></PermissionRoute>} />
          <Route path="/production/lines/new" element={<PermissionRoute permission="production.lines"><ProductionLineFormPage /></PermissionRoute>} />
          <Route path="/production/lines/:id/edit" element={<PermissionRoute permission="production.lines"><ProductionLineFormPage /></PermissionRoute>} />
          <Route path="/production/lines/:id" element={<PermissionRoute permission="production.view"><ProductionLineDetailPage /></PermissionRoute>} />
          <Route path="/production/orders" element={<PermissionRoute permission="production.view"><ProductionOrdersPage /></PermissionRoute>} />
          <Route path="/production/orders/new" element={<PermissionRoute permission="production.create"><ProductionOrderFormPage /></PermissionRoute>} />
          <Route path="/production/orders/:id/edit" element={<PermissionRoute permission="production.edit"><ProductionOrderFormPage /></PermissionRoute>} />
          <Route path="/production/orders/:id" element={<PermissionRoute permission="production.view"><ProductionOrderDetailPage /></PermissionRoute>} />
          <Route path="/production/packaging" element={<PermissionRoute permission="production.packaging"><PackagingPage /></PermissionRoute>} />
          <Route path="/production/packaging/new" element={<PermissionRoute permission="production.packaging"><PackagingFormPage /></PermissionRoute>} />
          <Route path="/production/packaging/:id/edit" element={<PermissionRoute permission="production.packaging"><PackagingFormPage /></PermissionRoute>} />
          <Route path="/production/packaging/:id" element={<PermissionRoute permission="production.packaging"><PackagingDetailPage /></PermissionRoute>} />

          {/* Sales Routes */}
          <Route path="/sales" element={<Navigate to="/sales/orders" replace />} />
          <Route path="/sales/orders" element={<PermissionRoute anyOf={["sales.orders.view", "sales.view"]}><SalesOrdersPage /></PermissionRoute>} />
          <Route path="/sales/orders/new" element={<PermissionRoute permission="sales.orders.create"><SalesOrderFormPage /></PermissionRoute>} />
          <Route path="/sales/orders/:id/edit" element={<PermissionRoute permission="sales.orders.edit"><SalesOrderFormPage /></PermissionRoute>} />
          <Route path="/sales/orders/:id" element={<PermissionRoute anyOf={["sales.orders.view", "sales.view"]}><SalesOrderDetailPage /></PermissionRoute>} />
          <Route path="/sales/customers" element={<PermissionRoute anyOf={["sales.customers.view", "sales.view"]}><CustomersPage /></PermissionRoute>} />
          
          {/* Quality Routes */}
          <Route path="/quality" element={<PermissionRoute permission="quality.view"><QualityPage /></PermissionRoute>} />
          <Route path="/quality/inspections/new" element={<PermissionRoute permission="quality.inspect"><InspectionFormPage /></PermissionRoute>} />
          <Route path="/quality/inspections/:id" element={<PermissionRoute permission="quality.view"><InspectionFormPage /></PermissionRoute>} />
          <Route path="/quality/inspections/:id/edit" element={<PermissionRoute permission="quality.inspect"><InspectionFormPage /></PermissionRoute>} />
          <Route path="/quality/ncrs/new" element={<PermissionRoute permission="quality.ncr_create"><NCRFormPage /></PermissionRoute>} />
          <Route path="/quality/ncrs/:id" element={<PermissionRoute permission="quality.view"><NCRFormPage /></PermissionRoute>} />
          <Route path="/quality/ncrs/:id/edit" element={<PermissionRoute permission="quality.ncr_create"><NCRFormPage /></PermissionRoute>} />
          
          {/* Reports Routes */}
          <Route path="/reports" element={<PermissionRoute permission="reports.view"><ReportsPage /></PermissionRoute>} />
          
          {/* Settings Routes */}
          <Route path="/settings" element={<PermissionRoute permission="settings.view"><SettingsPage /></PermissionRoute>} />
          
          {/* Profile Routes */}
          <Route path="/profile" element={<ProfilePage />} />

          {/* Notifications Route */}
          <Route path="/notifications" element={<NotificationsPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
