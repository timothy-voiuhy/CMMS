import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Settings, Building, Globe, Clock, Plus, Edit, Trash2, Save, Shield, Zap, Key } from 'lucide-react'
import { companyService } from '../../services/company.service'
import { permissionsService } from '../../services/permissions.service'
import { useAuthStore } from '../../store/authStore'
import PermissionEditor from '../../components/settings/PermissionEditor'
import type {
  Company,
  UpdateCompanyRequest,
  Facility,
  Department,
  Role
} from '../../services/company.service'
import type { RoleTemplate } from '../../types/permissions'
import { ROLE_TEMPLATES } from '../../config/permissions'

type TabType = 'company' | 'business' | 'operational' | 'facilities' | 'departments' | 'roles'

const VALID_TABS: TabType[] = ['company', 'business', 'operational', 'facilities', 'departments', 'roles']

const SettingsPage = () => {
  const { user } = useAuthStore()
  const isSystemAdmin = user?.role?.toLowerCase() === 'admin'
  const [searchParams, setSearchParams] = useSearchParams()

  const getInitialTab = (): TabType => {
    const paramTab = searchParams.get('tab') as TabType
    if (paramTab && VALID_TABS.includes(paramTab)) return paramTab

    const localTab = localStorage.getItem('icms_settings_tab') as TabType
    if (localTab && VALID_TABS.includes(localTab)) return localTab

    return 'company'
  }

  const [activeTab, setActiveTabState] = useState<TabType>(getInitialTab)

  const setActiveTab = (tab: TabType) => {
    setActiveTabState(tab)
    setSearchParams({ tab }, { replace: true })
    localStorage.setItem('icms_settings_tab', tab)
  }

  useEffect(() => {
    const paramTab = searchParams.get('tab') as TabType
    if (paramTab && VALID_TABS.includes(paramTab) && paramTab !== activeTab) {
      setActiveTabState(paramTab)
      localStorage.setItem('icms_settings_tab', paramTab)
    }
  }, [searchParams])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Company state
  const [company, setCompany] = useState<Company | null>(null)
  const [companyForm, setCompanyForm] = useState<UpdateCompanyRequest>({})

  // Facility state
  const [facilities, setFacilities] = useState<Facility[]>([])
  const [facilityDialog, setFacilityDialog] = useState(false)
  const [editingFacility, setEditingFacility] = useState<Facility | null>(null)
  const [facilityForm, setFacilityForm] = useState<any>({
    company_id: 0,
    name: '',
    facility_type: 'plant',
    facility_code: ''
  })

  // Department state
  const [departments, setDepartments] = useState<Department[]>([])
  const [departmentDialog, setDepartmentDialog] = useState(false)
  const [editingDepartment, setEditingDepartment] = useState<Department | null>(null)
  const [departmentForm, setDepartmentForm] = useState<any>({
    facility_id: 0,
    name: '',
    department_code: ''
  })

  // Role state
  const [roles, setRoles] = useState<Role[]>([])
  const [roleDialog, setRoleDialog] = useState(false)
  const [editingRole, setEditingRole] = useState<Role | null>(null)
  const [roleForm, setRoleForm] = useState<any>({
    name: '',
    description: '',
    level: 1,
    category: '',
    is_active: true
  })
  // Permission state
  const [rolePermissions, setRolePermissions] = useState<string[]>([])
  const [templateDialog, setTemplateDialog] = useState(false)
  const [templateForm, setTemplateForm] = useState<any>({
    name: '',
    template: '',
    description: '',
  })

  useEffect(() => {
    loadCompany()
    loadFacilities()
    loadDepartments()
    loadRoles()
  }, [])

  useEffect(() => {
    if (company) {
      setCompanyForm({
        name: company.name,
        short_name: company.short_name,
        industry_type: company.industry_type,
        registration_number: company.registration_number,
        tax_id: company.tax_id,
        address: company.address,
        city: company.city,
        country: company.country,
        phone: company.phone,
        email: company.email,
        website: company.website,
        currency: company.currency,
        timezone: company.timezone,
        language: company.language,
        working_hours_start: company.working_hours_start,
        working_hours_end: company.working_hours_end,
        working_days: company.working_days,
        is_active: company.is_active
      })
    }
  }, [company])

  const loadCompany = async () => {
    try {
      setLoading(true)
      const data = await companyService.getCompany()
      setCompany(data)
      setError(null)
    } catch (err: any) {
      if (err.response?.status !== 404) {
        setError('Failed to load company information')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadFacilities = async () => {
    try {
      const data = await companyService.getFacilities()
      setFacilities(data)
    } catch (err) {
      console.error('Failed to load facilities:', err)
    }
  }

  const loadDepartments = async () => {
    try {
      const data = await companyService.getDepartments()
      setDepartments(data)
    } catch (err) {
      console.error('Failed to load departments:', err)
    }
  }

  const loadRoles = async () => {
    try {
      const data = await companyService.getRoles()
      setRoles(data)
    } catch (err) {
      console.error('Failed to load roles:', err)
    }
  }

  const handleSaveCompany = async () => {
    if (!company) return

    try {
      setLoading(true)
      await companyService.updateCompany(company.id, companyForm)
      setSuccess('Company information updated successfully')
      setTimeout(() => setSuccess(null), 3000)
      loadCompany()
    } catch (err) {
      setError('Failed to update company information')
      setTimeout(() => setError(null), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleOpenFacilityDialog = (facility?: Facility) => {
    if (facility) {
      setEditingFacility(facility)
      setFacilityForm({
        name: facility.name,
        facility_type: facility.facility_type,
        facility_code: facility.facility_code,
        address: facility.address,
        city: facility.city,
        country: facility.country,
        gps_coordinates: facility.gps_coordinates,
        phone: facility.phone,
        manager_name: facility.manager_name,
        manager_contact: facility.manager_contact,
        is_active: facility.is_active,
        notes: facility.notes
      })
    } else {
      setEditingFacility(null)
      setFacilityForm({
        company_id: company?.id || 0,
        name: '',
        facility_type: 'plant',
        facility_code: '',
        is_active: true
      })
    }
    setFacilityDialog(true)
  }

  const handleSaveFacility = async () => {
    try {
      setLoading(true)
      if (editingFacility) {
        await companyService.updateFacility(editingFacility.id, facilityForm)
        setSuccess('Facility updated successfully')
      } else {
        await companyService.createFacility(facilityForm)
        setSuccess('Facility created successfully')
      }
      setTimeout(() => setSuccess(null), 3000)
      loadFacilities()
      setFacilityDialog(false)
    } catch (err) {
      setError('Failed to save facility')
      setTimeout(() => setError(null), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteFacility = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this facility?')) return

    try {
      await companyService.deleteFacility(id)
      setSuccess('Facility deleted successfully')
      setTimeout(() => setSuccess(null), 3000)
      loadFacilities()
    } catch (err) {
      setError('Failed to delete facility')
      setTimeout(() => setError(null), 3000)
    }
  }

  const handleOpenDepartmentDialog = (department?: Department) => {
    if (department) {
      setEditingDepartment(department)
      setDepartmentForm({
        name: department.name,
        department_code: department.department_code,
        description: department.description,
        manager_name: department.manager_name,
        cost_center: department.cost_center,
        is_active: department.is_active
      })
    } else {
      setEditingDepartment(null)
      setDepartmentForm({
        facility_id: facilities[0]?.id || 0,
        name: '',
        department_code: '',
        is_active: true
      })
    }
    setDepartmentDialog(true)
  }

  const handleSaveDepartment = async () => {
    try {
      setLoading(true)
      if (editingDepartment) {
        await companyService.updateDepartment(editingDepartment.id, departmentForm)
        setSuccess('Department updated successfully')
      } else {
        await companyService.createDepartment(departmentForm)
        setSuccess('Department created successfully')
      }
      setTimeout(() => setSuccess(null), 3000)
      loadDepartments()
      setDepartmentDialog(false)
    } catch (err) {
      setError('Failed to save department')
      setTimeout(() => setError(null), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDepartment = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this department?')) return

    try {
      await companyService.deleteDepartment(id)
      setSuccess('Department deleted successfully')
      setTimeout(() => setSuccess(null), 3000)
      loadDepartments()
    } catch (err) {
      setError('Failed to delete department')
      setTimeout(() => setError(null), 3000)
    }
  }

  const handleOpenRoleDialog = async (role?: Role) => {
    if (role) {
      setEditingRole(role)
      setRoleForm({
        name: role.name,
        description: role.description,
        level: role.level,
        category: role.category,
        is_active: role.is_active,
        is_system_role: role.is_system_role,
      })
      // Load parsed permissions for this role
      try {
        const roleWithPerms = await permissionsService.getRolePermissions(role.id)
        setRolePermissions(roleWithPerms.parsed_permissions || [])
      } catch {
        // Fall back to parsing permissions_json directly
        try {
          const parsed = role.permissions_json ? JSON.parse(role.permissions_json) : null
          setRolePermissions(parsed?.permissions || [])
        } catch {
          setRolePermissions([])
        }
      }
    } else {
      setEditingRole(null)
      setRoleForm({
        name: '',
        description: '',
        level: 1,
        category: '',
        is_active: true,
        is_system_role: false,
      })
      setRolePermissions([])
    }
    setRoleDialog(true)
  }

  const handleSaveRole = async () => {
    try {
      setLoading(true)
      if (editingRole) {
        await companyService.updateRole(editingRole.id, roleForm)
        // Save permissions separately
        await permissionsService.updateRolePermissions(editingRole.id, {
          permissions: rolePermissions,
          custom: true,
        })
        setSuccess('Role updated successfully')
      } else {
        const newRole = await companyService.createRole(roleForm)
        // Save permissions for the new role
        if (rolePermissions.length > 0) {
          await permissionsService.updateRolePermissions(newRole.id, {
            permissions: rolePermissions,
            custom: true,
          })
        }
        setSuccess('Role created successfully')
      }
      setTimeout(() => setSuccess(null), 3000)
      loadRoles()
      setRoleDialog(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save role')
      setTimeout(() => setError(null), 3000)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateFromTemplate = async () => {
    if (!templateForm.name || !templateForm.template) return
    try {
      setLoading(true)
      await permissionsService.createRoleFromTemplate({
        name: templateForm.name,
        template: templateForm.template,
        description: templateForm.description || undefined,
      })
      setSuccess('Role created from template successfully')
      setTimeout(() => setSuccess(null), 3000)
      loadRoles()
      setTemplateDialog(false)
      setTemplateForm({ name: '', template: '', description: '' })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create role from template')
      setTimeout(() => setError(null), 3000)
    } finally {
      setLoading(false)
    }
  }

  const getRolePermissionCount = (role: Role): number => {
    if (!role.permissions_json) return 0
    try {
      const parsed = JSON.parse(role.permissions_json)
      return (parsed.permissions || []).length
    } catch {
      return 0
    }
  }

  const handleDeleteRole = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this role?')) return

    try {
      await companyService.deleteRole(id)
      setSuccess('Role deleted successfully')
      setTimeout(() => setSuccess(null), 3000)
      loadRoles()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete role')
      setTimeout(() => setError(null), 3000)
    }
  }


  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Settings className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Company Settings</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Manage company information and configuration</p>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-800 dark:text-red-300">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-800 dark:text-green-300">
            {success}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('company')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'company'
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
            >
              <div className="flex items-center gap-2">
                <Building className="w-4 h-4" />
                Company Info
              </div>
            </button>
            <button
              onClick={() => setActiveTab('business')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'business'
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
            >
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4" />
                Business Settings
              </div>
            </button>
            <button
              onClick={() => setActiveTab('operational')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'operational'
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
            >
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Operational
              </div>
            </button>
            <button
              onClick={() => setActiveTab('facilities')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'facilities'
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
            >
              <div className="flex items-center gap-2">
                <Building className="w-4 h-4" />
                Facilities
              </div>
            </button>
            <button
              onClick={() => setActiveTab('departments')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'departments'
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
            >
              <div className="flex items-center gap-2">
                <Building className="w-4 h-4" />
                Departments
              </div>
            </button>
            <button
              onClick={() => setActiveTab('roles')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'roles'
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
            >
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Roles
              </div>
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Company Information Tab */}
          {activeTab === 'company' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Company Name</label>
                  <input
                    type="text"
                    value={companyForm.name || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Short Name</label>
                  <input
                    type="text"
                    value={companyForm.short_name || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, short_name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Industry Type</label>
                  <input
                    type="text"
                    value={companyForm.industry_type || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, industry_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Registration Number</label>
                  <input
                    type="text"
                    value={companyForm.registration_number || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, registration_number: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tax ID</label>
                  <input
                    type="text"
                    value={companyForm.tax_id || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, tax_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Address</label>
                  <textarea
                    value={companyForm.address || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, address: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">City</label>
                  <input
                    type="text"
                    value={companyForm.city || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, city: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Country</label>
                  <input
                    type="text"
                    value={companyForm.country || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, country: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Phone</label>
                  <input
                    type="text"
                    value={companyForm.phone || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, phone: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label>
                  <input
                    type="email"
                    value={companyForm.email || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Website</label>
                  <input
                    type="text"
                    value={companyForm.website || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, website: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
              <button
                onClick={handleSaveCompany}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                Save Company Information
              </button>
            </div>
          )}


          {/* Business Settings Tab */}
          {activeTab === 'business' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Currency</label>
                  <select
                    value={companyForm.currency || 'USD'}
                    onChange={(e) => setCompanyForm({ ...companyForm, currency: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="USD">USD - US Dollar</option>
                    <option value="EUR">EUR - Euro</option>
                    <option value="GBP">GBP - British Pound</option>
                    <option value="UGX">UGX - Ugandan Shilling</option>
                    <option value="KES">KES - Kenyan Shilling</option>
                    <option value="TZS">TZS - Tanzanian Shilling</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Timezone</label>
                  <select
                    value={companyForm.timezone || 'UTC'}
                    onChange={(e) => setCompanyForm({ ...companyForm, timezone: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="UTC">UTC</option>
                    <option value="Africa/Nairobi">Africa/Nairobi (EAT)</option>
                    <option value="Africa/Lagos">Africa/Lagos (WAT)</option>
                    <option value="Africa/Johannesburg">Africa/Johannesburg (SAST)</option>
                    <option value="America/New_York">America/New_York (EST)</option>
                    <option value="Europe/London">Europe/London (GMT)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Language</label>
                  <select
                    value={companyForm.language || 'en'}
                    onChange={(e) => setCompanyForm({ ...companyForm, language: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="en">English</option>
                    <option value="fr">French</option>
                    <option value="sw">Swahili</option>
                  </select>
                </div>
              </div>
              <button
                onClick={handleSaveCompany}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                Save Business Settings
              </button>
            </div>
          )}

          {/* Operational Settings Tab */}
          {activeTab === 'operational' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Working Hours Start</label>
                  <input
                    type="time"
                    value={companyForm.working_hours_start || '08:00'}
                    onChange={(e) => setCompanyForm({ ...companyForm, working_hours_start: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Working Hours End</label>
                  <input
                    type="time"
                    value={companyForm.working_hours_end || '17:00'}
                    onChange={(e) => setCompanyForm({ ...companyForm, working_hours_end: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Working Days (JSON format)</label>
                  <input
                    type="text"
                    value={companyForm.working_days || ''}
                    onChange={(e) => setCompanyForm({ ...companyForm, working_days: e.target.value })}
                    placeholder='["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]'
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  />
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Enter working days as JSON array</p>
                </div>
                <div className="md:col-span-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={companyForm.is_active !== false}
                      onChange={(e) => setCompanyForm({ ...companyForm, is_active: e.target.checked })}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Company Active</span>
                  </label>
                </div>
              </div>
              <button
                onClick={handleSaveCompany}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                Save Operational Settings
              </button>
            </div>
          )}

          {/* Facilities Tab */}
          {activeTab === 'facilities' && (
            <div className="space-y-6">
              <button
                onClick={() => handleOpenFacilityDialog()}
                disabled={!company}
                className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                <Plus className="w-4 h-4" />
                Add Facility
              </button>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Code</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">City</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Manager</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {facilities.map((facility) => (
                      <tr key={facility.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{facility.facility_code}</td>
                        <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-gray-100">{facility.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 rounded-full">
                            {facility.facility_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{facility.city}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{facility.manager_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${facility.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400' : 'bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-300'
                            }`}>
                            {facility.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          <button
                            onClick={() => handleOpenFacilityDialog(facility)}
                            className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 mr-3"
                          >
                            <Edit className="w-4 h-4 inline" />
                          </button>
                          <button
                            onClick={() => handleDeleteFacility(facility.id)}
                            className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                          >
                            <Trash2 className="w-4 h-4 inline" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Departments Tab */}
          {activeTab === 'departments' && (
            <div className="space-y-6">
              <button
                onClick={() => handleOpenDepartmentDialog()}
                disabled={facilities.length === 0}
                className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                <Plus className="w-4 h-4" />
                Add Department
              </button>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Code</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Facility</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Manager</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Cost Center</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {departments.map((department) => (
                      <tr key={department.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{department.department_code}</td>
                        <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-gray-100">{department.name}</td>
                        <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                          {facilities.find(f => f.id === department.facility_id)?.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{department.manager_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{department.cost_center}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${department.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400' : 'bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-300'
                            }`}>
                            {department.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                          <button
                            onClick={() => handleOpenDepartmentDialog(department)}
                            className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 mr-3"
                          >
                            <Edit className="w-4 h-4 inline" />
                          </button>
                          <button
                            onClick={() => handleDeleteDepartment(department.id)}
                            className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
                          >
                            <Trash2 className="w-4 h-4 inline" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Roles Tab */}
          {activeTab === 'roles' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Manage roles, permissions, and hierarchy. System roles cannot be modified or deleted.
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setTemplateDialog(true)}
                    className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
                  >
                    <Zap className="w-4 h-4" />
                    From Template
                  </button>
                  <button
                    onClick={() => handleOpenRoleDialog()}
                    className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
                  >
                    <Plus className="w-4 h-4" />
                    Add Role
                  </button>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Level</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Category</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Permissions</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {roles.map((role) => {
                      const permCount = getRolePermissionCount(role)
                      return (
                        <tr key={role.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                          <td className="px-6 py-4">
                            <div>
                              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{role.name}</span>
                              {role.description && (
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{role.description}</p>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="px-2 py-1 text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400 rounded-full">
                              L{role.level}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">{role.category || '-'}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-1.5">
                              <Key className="w-3.5 h-3.5 text-gray-400" />
                              <span className="text-sm text-gray-700 dark:text-gray-300">
                                {permCount > 0 ? `${permCount} permissions` : 'No permissions'}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {role.is_system_role ? (
                              <span className="px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 rounded-full">
                                System
                              </span>
                            ) : (
                              <span className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full">
                                Custom
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${role.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400' : 'bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-300'
                              }`}>
                              {role.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                            <button
                              onClick={() => handleOpenRoleDialog(role)}
                              disabled={role.is_system_role && !isSystemAdmin}
                              className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300 mr-3 disabled:opacity-50 disabled:cursor-not-allowed"
                              title={role.is_system_role && !isSystemAdmin ? "Only System Administrators can edit system roles" : "Edit role & permissions"}
                            >
                              <Edit className="w-4 h-4 inline" />
                            </button>
                            <button
                              onClick={() => handleDeleteRole(role.id)}
                              disabled={role.is_system_role && !isSystemAdmin}
                              className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed"
                              title={role.is_system_role && !isSystemAdmin ? "Only System Administrators can delete system roles" : "Delete role"}
                            >
                              <Trash2 className="w-4 h-4 inline" />
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>


      {/* Facility Dialog */}
      {facilityDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl mx-4">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                {editingFacility ? 'Edit Facility' : 'Add Facility'}
              </h3>
            </div>
            <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name</label>
                  <input
                    type="text"
                    value={facilityForm.name || ''}
                    onChange={(e) => setFacilityForm({ ...facilityForm, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Facility Code</label>
                  <input
                    type="text"
                    value={facilityForm.facility_code || ''}
                    onChange={(e) => setFacilityForm({ ...facilityForm, facility_code: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Facility Type</label>
                  <select
                    value={facilityForm.facility_type || 'plant'}
                    onChange={(e) => setFacilityForm({ ...facilityForm, facility_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="plant">Plant</option>
                    <option value="warehouse">Warehouse</option>
                    <option value="office">Office</option>
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Address</label>
                  <textarea
                    value={facilityForm.address || ''}
                    onChange={(e) => setFacilityForm({ ...facilityForm, address: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">City</label>
                  <input
                    type="text"
                    value={facilityForm.city || ''}
                    onChange={(e) => setFacilityForm({ ...facilityForm, city: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Country</label>
                  <input
                    type="text"
                    value={facilityForm.country || ''}
                    onChange={(e) => setFacilityForm({ ...facilityForm, country: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Manager Name</label>
                  <input
                    type="text"
                    value={facilityForm.manager_name || ''}
                    onChange={(e) => setFacilityForm({ ...facilityForm, manager_name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Manager Contact</label>
                  <input
                    type="text"
                    value={facilityForm.manager_contact || ''}
                    onChange={(e) => setFacilityForm({ ...facilityForm, manager_contact: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Notes</label>
                  <textarea
                    value={facilityForm.notes || ''}
                    onChange={(e) => setFacilityForm({ ...facilityForm, notes: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
            </div>
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
              <button
                onClick={() => setFacilityDialog(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveFacility}
                className="px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Department Dialog */}
      {departmentDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                {editingDepartment ? 'Edit Department' : 'Add Department'}
              </h3>
            </div>
            <div className="px-6 py-4">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Facility</label>
                  <select
                    value={departmentForm.facility_id || ''}
                    onChange={(e) => setDepartmentForm({ ...departmentForm, facility_id: parseInt(e.target.value) })}
                    disabled={!!editingDepartment}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  >
                    <option value="">Select Facility</option>
                    {facilities.map((facility) => (
                      <option key={facility.id} value={facility.id}>
                        {facility.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name</label>
                  <input
                    type="text"
                    value={departmentForm.name || ''}
                    onChange={(e) => setDepartmentForm({ ...departmentForm, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Department Code</label>
                  <input
                    type="text"
                    value={departmentForm.department_code || ''}
                    onChange={(e) => setDepartmentForm({ ...departmentForm, department_code: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
                  <textarea
                    value={departmentForm.description || ''}
                    onChange={(e) => setDepartmentForm({ ...departmentForm, description: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Manager Name</label>
                  <input
                    type="text"
                    value={departmentForm.manager_name || ''}
                    onChange={(e) => setDepartmentForm({ ...departmentForm, manager_name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Cost Center</label>
                  <input
                    type="text"
                    value={departmentForm.cost_center || ''}
                    onChange={(e) => setDepartmentForm({ ...departmentForm, cost_center: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>
              </div>
            </div>
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
              <button
                onClick={() => setDepartmentDialog(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveDepartment}
                className="px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Role Dialog — Enhanced with Permission Editor */}
      {roleDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] flex flex-col">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shield className="w-5 h-5 text-blue-500" />
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                  {editingRole ? 'Edit Role & Permissions' : 'Create New Role'}
                </h3>
              </div>
              <button
                onClick={() => setRoleDialog(false)}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <span className="text-gray-400 text-xl">&times;</span>
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {/* Role Details Section */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-3">Role Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Role Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={roleForm.name || ''}
                      onChange={(e) => setRoleForm({ ...roleForm, name: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      placeholder="e.g., Senior Technician"
                    />
                  </div>
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Level <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        required
                        min="1"
                        max="10"
                        value={roleForm.level || 1}
                        onChange={(e) => setRoleForm({ ...roleForm, level: parseInt(e.target.value) })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      />
                    </div>
                    <div className="flex-1">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
                      <select
                        value={roleForm.category || ''}
                        onChange={(e) => setRoleForm({ ...roleForm, category: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      >
                        <option value="">Select category</option>
                        <option value="Management">Management</option>
                        <option value="Supervision">Supervision</option>
                        <option value="Technical">Technical</option>
                        <option value="Operations">Operations</option>
                        <option value="Administration">Administration</option>
                      </select>
                    </div>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
                    <input
                      type="text"
                      value={roleForm.description || ''}
                      onChange={(e) => setRoleForm({ ...roleForm, description: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      placeholder="Brief description of this role"
                    />
                  </div>
                  <div className="flex flex-wrap gap-6">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={roleForm.is_active !== false}
                        onChange={(e) => setRoleForm({ ...roleForm, is_active: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Role Active</span>
                    </label>

                    {isSystemAdmin && (
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={!!roleForm.is_system_role}
                          onChange={(e) => setRoleForm({ ...roleForm, is_system_role: e.target.checked })}
                          className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                        />
                        <span className="text-sm font-medium text-blue-800 dark:text-blue-400 flex items-center gap-1">
                          <Shield className="w-3.5 h-3.5" />
                          System Role (Protected Core Role)
                        </span>
                      </label>
                    )}
                  </div>
                </div>
              </div>

              {/* Permissions Section */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-3">Permissions</h4>
                <PermissionEditor
                  permissions={rolePermissions}
                  onChange={setRolePermissions}
                />
              </div>
            </div>
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
              <button
                onClick={() => setRoleDialog(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveRole}
                disabled={!roleForm.name || loading}
                className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                <Save className="w-4 h-4" />
                {loading ? 'Saving...' : 'Save Role & Permissions'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Template Dialog */}
      {templateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-lg mx-4">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-500" />
                Create Role from Template
              </h3>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Template <span className="text-red-500">*</span>
                </label>
                <select
                  value={templateForm.template}
                  onChange={(e) => {
                    const key = e.target.value
                    const tpl = ROLE_TEMPLATES[key]
                    setTemplateForm({
                      ...templateForm,
                      template: key,
                      description: tpl?.description || '',
                    })
                  }}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="">Select a template...</option>
                  {Object.entries(ROLE_TEMPLATES).map(([key, tpl]) => (
                    <option key={key} value={key}>
                      {tpl.name} (L{tpl.level} - {tpl.category})
                    </option>
                  ))}
                </select>
                {templateForm.template && ROLE_TEMPLATES[templateForm.template] && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {ROLE_TEMPLATES[templateForm.template].permissions.length} permissions included
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Role Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={templateForm.name}
                  onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="e.g., Factory Floor Manager"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
                <input
                  type="text"
                  value={templateForm.description}
                  onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  placeholder="Optional description"
                />
              </div>
            </div>
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
              <button
                onClick={() => setTemplateDialog(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateFromTemplate}
                disabled={!templateForm.name || !templateForm.template || loading}
                className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50"
              >
                <Zap className="w-4 h-4" />
                {loading ? 'Creating...' : 'Create Role'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SettingsPage
