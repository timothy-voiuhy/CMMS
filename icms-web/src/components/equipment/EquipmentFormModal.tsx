import React, { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import type { Equipment } from '../../types'
import type { CreateEquipmentRequest } from '../../services/equipment.service'

interface EquipmentFormModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: CreateEquipmentRequest) => Promise<void>
  equipment?: Equipment
  isLoading?: boolean
}

const EquipmentFormModal: React.FC<EquipmentFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  equipment,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<CreateEquipmentRequest>({
    name: '',
    equipment_id: '',
    category: '',
    manufacturer: '',
    model: '',
    serial_number: '',
    location: '',
    status: 'OPERATIONAL',
    purchase_date: '',
    warranty_expiry: '',
    specifications: '',
    notes: '',
  })

  useEffect(() => {
    if (equipment) {
      setFormData({
        name: equipment.name,
        equipment_id: equipment.equipment_id,
        category: equipment.category,
        manufacturer: equipment.manufacturer,
        model: equipment.model,
        serial_number: equipment.serial_number,
        location: equipment.location,
        status: equipment.status,
        purchase_date: equipment.purchase_date,
        warranty_expiry: equipment.warranty_expiry,
        specifications: equipment.specifications,
        notes: equipment.notes,
      })
    } else {
      setFormData({
        name: '',
        equipment_id: '',
        category: '',
        manufacturer: '',
        model: '',
        serial_number: '',
        location: '',
        status: 'OPERATIONAL',
        purchase_date: '',
        warranty_expiry: '',
        specifications: '',
        notes: '',
      })
    }
  }, [equipment])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit(formData)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          {/* Header */}
          <div className="bg-white px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                {equipment ? 'Edit Equipment' : 'Add New Equipment'}
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-500 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="bg-white px-6 py-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[60vh] overflow-y-auto">
              {/* Name */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Equipment Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Potato Washing Machine"
                />
              </div>

              {/* Equipment ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Equipment ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.equipment_id}
                  onChange={(e) => setFormData({ ...formData, equipment_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., EQP-PC-001"
                />
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select category</option>
                  <option value="Potato Crisps Line">Potato Crisps Line</option>
                  <option value="Fried Corn Line">Fried Corn Line</option>
                  <option value="Utilities">Utilities</option>
                  <option value="Conveyors">Conveyors</option>
                </select>
              </div>

              {/* Manufacturer */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Manufacturer
                </label>
                <input
                  type="text"
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Model */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model
                </label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Serial Number */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Serial Number
                </label>
                <input
                  type="text"
                  value={formData.serial_number}
                  onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Location */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <select
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select location</option>
                  <option value="Production Line 1">Production Line 1</option>
                  <option value="Production Line 2">Production Line 2</option>
                  <option value="Generator House">Generator House</option>
                  <option value="Tank Farm">Tank Farm</option>
                  <option value="Well 1">Well 1</option>
                  <option value="Well 2">Well 2</option>
                  <option value="Well 3">Well 3</option>
                </select>
              </div>

              {/* Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="OPERATIONAL">Operational</option>
                  <option value="MAINTENANCE">Maintenance</option>
                  <option value="BREAKDOWN">Breakdown</option>
                  <option value="RETIRED">Retired</option>
                </select>
              </div>

              {/* Purchase Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Purchase Date
                </label>
                <input
                  type="date"
                  value={formData.purchase_date}
                  onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Warranty Expiry */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Warranty Expiry
                </label>
                <input
                  type="date"
                  value={formData.warranty_expiry}
                  onChange={(e) => setFormData({ ...formData, warranty_expiry: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Specifications */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Specifications
                </label>
                <textarea
                  rows={2}
                  value={formData.specifications}
                  onChange={(e) => setFormData({ ...formData, specifications: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Technical specifications..."
                />
              </div>

              {/* Notes */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  rows={2}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Additional notes..."
                />
              </div>
            </div>

            {/* Footer */}
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Saving...' : equipment ? 'Update Equipment' : 'Add Equipment'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default EquipmentFormModal
