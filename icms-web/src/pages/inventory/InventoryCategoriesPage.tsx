import React, { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, FolderTree } from 'lucide-react'
import {
  inventoryService,
  type InventoryCategory,
  type InventoryCategoryTree,
  type CreateInventoryCategoryRequest,
  type UpdateInventoryCategoryRequest,
} from '../../services/inventory.service'

const InventoryCategoriesPage: React.FC = () => {
  const [categories, setCategories] = useState<InventoryCategory[]>([])
  const [categoryTree, setCategoryTree] = useState<InventoryCategoryTree[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingCategory, setEditingCategory] = useState<InventoryCategory | null>(null)
  const [formData, setFormData] = useState<CreateInventoryCategoryRequest>({
    name: '',
    description: '',
    parent_id: undefined,
    is_active: true,
  })

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      setIsLoading(true)
      const [flatCategories, tree] = await Promise.all([
        inventoryService.getCategories(true), // Include inactive
        inventoryService.getCategoryTree(),
      ])
      setCategories(flatCategories)
      setCategoryTree(tree)
    } catch (error) {
      console.error('Failed to load categories:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingCategory(null)
    setFormData({
      name: '',
      description: '',
      parent_id: undefined,
      is_active: true,
    })
    setShowModal(true)
  }

  const handleEdit = (category: InventoryCategory) => {
    setEditingCategory(category)
    setFormData({
      name: category.name,
      description: category.description || '',
      parent_id: category.parent_id,
      is_active: category.is_active,
    })
    setShowModal(true)
  }

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"? This will deactivate it if it has items.`)) {
      return
    }

    try {
      await inventoryService.deleteCategory(id)
      await loadCategories()
    } catch (error) {
      console.error('Failed to delete category:', error)
      alert('Failed to delete category')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      if (editingCategory) {
        await inventoryService.updateCategory(editingCategory.id, formData as UpdateInventoryCategoryRequest)
      } else {
        await inventoryService.createCategory(formData)
      }
      setShowModal(false)
      await loadCategories()
    } catch (error: any) {
      console.error('Failed to save category:', error)
      alert(error.response?.data?.detail || 'Failed to save category')
    }
  }

  const renderTreeNode = (node: InventoryCategoryTree, level: number = 0): React.ReactNode => {
    const category = categories.find((c) => c.id === node.id)
    if (!category) return null

    return (
      <div key={node.id}>
        <div
          className={`flex items-center justify-between p-3 border rounded-lg mb-2 ${
            !category.is_active ? 'bg-gray-100 opacity-60' : 'bg-white'
          }`}
          style={{ marginLeft: `${level * 2}rem` }}
        >
          <div className="flex items-center gap-3">
            <FolderTree className="w-5 h-5 text-gray-400" />
            <div>
              <h3 className="font-medium text-gray-800">
                {category.name}
                {!category.is_active && (
                  <span className="ml-2 text-xs text-gray-500">(Inactive)</span>
                )}
              </h3>
              {category.description && (
                <p className="text-sm text-gray-600">{category.description}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleEdit(category)}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
              title="Edit"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleDelete(category.id, category.name)}
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
        {node.children && node.children.length > 0 && (
          <div>
            {node.children.map((child) => renderTreeNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Inventory Categories</h1>
          <p className="text-gray-600 mt-1">Manage hierarchical inventory categories</p>
        </div>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Category
        </button>
      </div>

      {/* Category Tree */}
      <div className="bg-white rounded-lg shadow p-6">
        {categoryTree.length === 0 ? (
          <div className="text-center py-12">
            <FolderTree className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500">No categories yet</p>
            <button
              onClick={handleCreate}
              className="mt-4 text-blue-600 hover:underline"
            >
              Create your first category
            </button>
          </div>
        ) : (
          <div>
            {categoryTree.map((node) => renderTreeNode(node))}
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              {editingCategory ? 'Edit Category' : 'Add Category'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Flavors"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Category description..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Parent Category
                  </label>
                  <select
                    value={formData.parent_id || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        parent_id: e.target.value ? parseInt(e.target.value) : undefined,
                      })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">None (Root Category)</option>
                    {categories
                      .filter((c) => c.id !== editingCategory?.id && c.is_active)
                      .map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.name}
                        </option>
                      ))}
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="is_active" className="text-sm text-gray-700">
                    Active
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingCategory ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default InventoryCategoriesPage
