import React, { useCallback, useEffect, useState } from 'react'
import { Plus, RefreshCw, Save, Search, Trash2, X } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { salesService, type Customer, type CreateCustomerRequest } from '../../services/sales.service'

const emptyCustomer: CreateCustomerRequest = {
  name: '',
  customer_code: '',
  contact_person: '',
  email: '',
  phone: '',
  billing_address: '',
  shipping_address: '',
  tax_id: '',
  payment_terms: '',
  credit_limit: undefined,
  is_active: true,
  notes: '',
}

const getErrorMessage = (error: unknown, fallback: string) => {
  const response = (error as { response?: { data?: { detail?: unknown } } }).response
  return typeof response?.data?.detail === 'string' ? response.data.detail : fallback
}

const CustomersPage: React.FC = () => {
  const { hasPermission } = useAuthStore()
  const [customers, setCustomers] = useState<Customer[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState({ page: 1, limit: 20, search: '', include_inactive: false })
  const [formData, setFormData] = useState<CreateCustomerRequest>(emptyCustomer)

  const canCreate = hasPermission('sales.customers.create')
  const canEdit = hasPermission('sales.customers.edit')
  const canDelete = hasPermission('sales.customers.delete')

  const loadCustomers = useCallback(async () => {
    try {
      setIsLoading(true)
      const response = await salesService.getCustomers({
        page: filters.page,
        limit: filters.limit,
        search: filters.search || undefined,
        include_inactive: filters.include_inactive,
      })
      setCustomers(response.data)
      setTotalPages(response.totalPages)
    } catch (error) {
      console.error('Failed to load customers:', error)
    } finally {
      setIsLoading(false)
    }
  }, [filters])

  useEffect(() => {
    void Promise.resolve().then(loadCustomers)
  }, [loadCustomers])

  const startCreate = () => {
    setEditingCustomer(null)
    setFormData(emptyCustomer)
    setShowForm(true)
  }

  const startEdit = (customer: Customer) => {
    setEditingCustomer(customer)
    setFormData({
      customer_code: customer.customer_code,
      name: customer.name,
      contact_person: customer.contact_person || '',
      email: customer.email || '',
      phone: customer.phone || '',
      billing_address: customer.billing_address || '',
      shipping_address: customer.shipping_address || '',
      tax_id: customer.tax_id || '',
      payment_terms: customer.payment_terms || '',
      credit_limit: customer.credit_limit,
      is_active: customer.is_active,
      notes: customer.notes || '',
    })
    setShowForm(true)
  }

  const buildPayload = (): CreateCustomerRequest => ({
    ...formData,
    customer_code: formData.customer_code || undefined,
    contact_person: formData.contact_person || undefined,
    email: formData.email || undefined,
    phone: formData.phone || undefined,
    billing_address: formData.billing_address || undefined,
    shipping_address: formData.shipping_address || undefined,
    tax_id: formData.tax_id || undefined,
    payment_terms: formData.payment_terms || undefined,
    credit_limit: formData.credit_limit || undefined,
    notes: formData.notes || undefined,
  })

  const handleSave = async () => {
    if (!formData.name.trim()) {
      alert('Customer name is required')
      return
    }

    try {
      setIsSaving(true)
      if (editingCustomer) {
        await salesService.updateCustomer(editingCustomer.id, buildPayload())
      } else {
        await salesService.createCustomer(buildPayload())
      }
      setShowForm(false)
      await loadCustomers()
    } catch (error: unknown) {
      console.error('Failed to save customer:', error)
      alert(getErrorMessage(error, 'Failed to save customer'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async (customer: Customer) => {
    if (!confirm(`Delete or deactivate ${customer.name}?`)) return
    try {
      await salesService.deleteCustomer(customer.id)
      await loadCustomers()
    } catch (error: unknown) {
      console.error('Failed to delete customer:', error)
      alert(getErrorMessage(error, 'Failed to delete customer'))
    }
  }

  return (
    <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Customers</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Manage sales customer records and contacts</p>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center sm:gap-3">
            <button
              onClick={loadCustomers}
              className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            {canCreate && (
              <button
                onClick={startCreate}
                className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600"
              >
                <Plus className="w-4 h-4" />
                New Customer
              </button>
            )}
          </div>
        </div>
      </div>

      {showForm && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
              {editingCustomer ? 'Edit Customer' : 'New Customer'}
            </h2>
            <button onClick={() => setShowForm(false)} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name</label>
              <input value={formData.name} onChange={(event) => setFormData({ ...formData, name: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Customer Code</label>
              <input value={formData.customer_code || ''} onChange={(event) => setFormData({ ...formData, customer_code: event.target.value })} placeholder="Auto-generated if empty" className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Contact Person</label>
              <input value={formData.contact_person || ''} onChange={(event) => setFormData({ ...formData, contact_person: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Phone</label>
              <input value={formData.phone || ''} onChange={(event) => setFormData({ ...formData, phone: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label>
              <input type="email" value={formData.email || ''} onChange={(event) => setFormData({ ...formData, email: event.target.value })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Payment Terms</label>
              <input value={formData.payment_terms || ''} onChange={(event) => setFormData({ ...formData, payment_terms: event.target.value })} placeholder="Net 30, Cash, COD..." className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Credit Limit</label>
              <input type="number" step="0.01" value={formData.credit_limit ?? ''} onChange={(event) => setFormData({ ...formData, credit_limit: event.target.value ? Number(event.target.value) : undefined })} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input type="checkbox" checked={formData.is_active ?? true} onChange={(event) => setFormData({ ...formData, is_active: event.target.checked })} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
              Active customer
            </label>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Billing Address</label>
              <textarea value={formData.billing_address || ''} onChange={(event) => setFormData({ ...formData, billing_address: event.target.value })} rows={2} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Shipping Address</label>
              <textarea value={formData.shipping_address || ''} onChange={(event) => setFormData({ ...formData, shipping_address: event.target.value })} rows={2} className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button onClick={handleSave} disabled={isSaving} className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50">
              <Save className="w-4 h-4" />
              Save Customer
            </button>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-4 md:items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                value={filters.search}
                onChange={(event) => setFilters({ ...filters, search: event.target.value, page: 1 })}
                placeholder="Search code, name, phone, or email..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 pb-2">
            <input type="checkbox" checked={filters.include_inactive} onChange={(event) => setFilters({ ...filters, include_inactive: event.target.checked, page: 1 })} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
            Include inactive
          </label>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-600 dark:text-gray-400">Loading customers...</div>
        ) : customers.length === 0 ? (
          <div className="p-8 text-center text-gray-600 dark:text-gray-400">No customers found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Customer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Contact</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Terms</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {customers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{customer.name}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{customer.customer_code}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                      <div>{customer.contact_person || '-'}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{customer.phone || customer.email || ''}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">{customer.payment_terms || '-'}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${customer.is_active ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}>
                        {customer.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {canEdit && <button onClick={() => startEdit(customer)} className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300">Edit</button>}
                        {canDelete && (
                          <button onClick={() => handleDelete(customer)} className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300" title="Delete">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <button onClick={() => setFilters({ ...filters, page: Math.max(1, filters.page - 1) })} disabled={filters.page === 1} className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 text-gray-700 dark:text-gray-200">Previous</button>
            <span className="text-sm text-gray-600 dark:text-gray-400">Page {filters.page} of {totalPages}</span>
            <button onClick={() => setFilters({ ...filters, page: Math.min(totalPages, filters.page + 1) })} disabled={filters.page === totalPages} className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 text-gray-700 dark:text-gray-200">Next</button>
          </div>
        )}
      </div>
    </div>
  )
}

export default CustomersPage
