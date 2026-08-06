import React, { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, ImageIcon, Save, Upload, X } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  maintenanceService,
  resolveCatalogueImageUrl,
  type CreateMaintenanceCatalogueItemRequest,
  type MaintenanceCatalogueItemType,
} from '../../services/maintenance.service'

const emptyItem = (): CreateMaintenanceCatalogueItemRequest => ({
  item_code: '',
  item_type: 'spare_part',
  name: '',
  description: '',
  category: '',
  image_url: '',
  manufacturer: '',
  model_number: '',
  supplier: '',
  unit_of_measure: '',
  unit_cost: undefined,
  location: '',
  compatible_equipment: '',
  inventory_item_id: undefined,
  is_active: true,
  notes: '',
})

const getErrorMessage = (error: unknown, fallback: string) => {
  const response = (error as { response?: { data?: { detail?: unknown } } }).response
  return typeof response?.data?.detail === 'string' ? response.data.detail : fallback
}

const fieldClass = 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500'

const MaintenanceCatalogueFormPage: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const itemId = id ? Number(id) : null
  const isEditMode = itemId != null && Number.isFinite(itemId)
  const [formData, setFormData] = useState<CreateMaintenanceCatalogueItemRequest>(emptyItem())
  const [categories, setCategories] = useState<string[]>([])
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [isLoading, setIsLoading] = useState(isEditMode)
  const [isSaving, setIsSaving] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')

  useEffect(() => {
    let isActive = true
    const load = async () => {
      try {
        const categoryValues = await maintenanceService.getCatalogueCategories()
        if (isActive) setCategories(categoryValues)
        if (!isEditMode || itemId == null) return
        const item = await maintenanceService.getCatalogueItemById(itemId)
        if (!isActive) return
        setFormData({
          item_code: item.item_code,
          item_type: item.item_type,
          name: item.name,
          description: item.description || '',
          category: item.category || '',
          image_url: item.image_url || '',
          manufacturer: item.manufacturer || '',
          model_number: item.model_number || '',
          supplier: item.supplier || '',
          unit_of_measure: item.unit_of_measure || '',
          unit_cost: item.unit_cost,
          location: item.location || '',
          compatible_equipment: item.compatible_equipment || '',
          inventory_item_id: item.inventory_item_id,
          is_active: item.is_active,
          notes: item.notes || '',
        })
      } catch (loadError) {
        if (isActive) setError(getErrorMessage(loadError, 'Failed to load catalogue item'))
      } finally {
        if (isActive) setIsLoading(false)
      }
    }
    void load()
    return () => { isActive = false }
  }, [isEditMode, itemId])

  useEffect(() => {
    if (!selectedImage) {
      setPreviewUrl('')
      return
    }
    const objectUrl = URL.createObjectURL(selectedImage)
    setPreviewUrl(objectUrl)
    return () => URL.revokeObjectURL(objectUrl)
  }, [selectedImage])

  const displayedImage = useMemo(
    () => previewUrl || resolveCatalogueImageUrl(formData.image_url),
    [formData.image_url, previewUrl],
  )

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Choose a JPEG, PNG, or WebP image')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be no larger than 10 MB')
      return
    }
    setError('')
    setSelectedImage(file)
  }

  const buildPayload = (imageUrl: string | null | undefined): CreateMaintenanceCatalogueItemRequest => ({
    ...formData,
    item_code: formData.item_code?.trim() || undefined,
    name: formData.name.trim(),
    description: formData.description?.trim() || undefined,
    category: formData.category?.trim() || undefined,
    image_url: imageUrl || undefined,
    manufacturer: formData.manufacturer?.trim() || undefined,
    model_number: formData.model_number?.trim() || undefined,
    supplier: formData.supplier?.trim() || undefined,
    unit_of_measure: formData.unit_of_measure?.trim() || undefined,
    unit_cost: formData.unit_cost ?? undefined,
    location: formData.location?.trim() || undefined,
    compatible_equipment: formData.compatible_equipment?.trim() || undefined,
    inventory_item_id: formData.inventory_item_id || undefined,
    notes: formData.notes?.trim() || undefined,
  })

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!formData.name.trim()) {
      setError('Name is required')
      return
    }
    try {
      setError('')
      setIsSaving(true)
      setUploadProgress(0)
      let imageUrl: string | null | undefined = formData.image_url === '' ? null : formData.image_url
      if (selectedImage) {
        const upload = await maintenanceService.uploadCatalogueImage(selectedImage, setUploadProgress)
        imageUrl = upload.image_url
      }
      const payload = buildPayload(imageUrl)
      if (isEditMode && itemId != null) {
        await maintenanceService.updateCatalogueItem(itemId, payload)
      } else {
        await maintenanceService.createCatalogueItem(payload)
      }
      navigate('/maintenance/catalogue')
    } catch (saveError) {
      setError(getErrorMessage(saveError, 'Failed to save catalogue item'))
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return <div className="p-8 text-center text-gray-600 dark:text-gray-400">Loading catalogue item...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="mb-6 flex items-start gap-3">
        <button onClick={() => navigate('/maintenance/catalogue')} className="mt-1 rounded-lg p-2 text-gray-600 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-700" aria-label="Back to catalogue">
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{isEditMode ? 'Edit Spare Part or Tool' : 'New Spare Part or Tool'}</h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">Manage catalogue details and upload a clear item image.</p>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">{error}</div>}

        <section className="rounded-lg border border-gray-200 bg-white p-4 shadow dark:border-gray-700 dark:bg-gray-800 sm:p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Item image</h2>
          <div className="grid gap-5 md:grid-cols-[280px_1fr]">
            <div className="aspect-[4/3] overflow-hidden rounded-lg border border-gray-200 bg-gray-100 dark:border-gray-600 dark:bg-gray-700">
              {displayedImage ? <img src={displayedImage} alt="Catalogue item preview" className="h-full w-full object-cover" /> : <div className="flex h-full items-center justify-center"><ImageIcon className="h-14 w-14 text-gray-400" /></div>}
            </div>
            <div className="flex flex-col justify-center gap-3">
              <p className="text-sm text-gray-600 dark:text-gray-400">JPEG, PNG, or WebP. Maximum size 10 MB.</p>
              <div className="flex flex-wrap gap-2">
                <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
                  <Upload className="h-4 w-4" />
                  {displayedImage ? 'Replace image' : 'Choose image'}
                  <input type="file" accept="image/jpeg,image/png,image/webp" onChange={handleImageChange} className="sr-only" />
                </label>
                {displayedImage && <button type="button" onClick={() => { setSelectedImage(null); setFormData({ ...formData, image_url: '' }) }} className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"><X className="h-4 w-4" />Remove</button>}
              </div>
              {selectedImage && <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Selected: {selectedImage.name}</p>}
              {isSaving && selectedImage && <div><div className="mb-1 text-xs text-gray-500">Uploading {uploadProgress}%</div><div className="h-2 overflow-hidden rounded bg-gray-200 dark:bg-gray-700"><div className="h-full bg-blue-600 transition-all" style={{ width: `${uploadProgress}%` }} /></div></div>}
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-4 shadow dark:border-gray-700 dark:bg-gray-800 sm:p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Catalogue details</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Name *</label><input required value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className={fieldClass} /></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Code</label><input value={formData.item_code || ''} onChange={(e) => setFormData({ ...formData, item_code: e.target.value })} placeholder="Auto-generated if empty" className={fieldClass} /></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Type *</label><select value={formData.item_type} onChange={(e) => setFormData({ ...formData, item_type: e.target.value as MaintenanceCatalogueItemType })} className={fieldClass}><option value="spare_part">Spare Part</option><option value="tool">Tool</option></select></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Category</label><input list="catalogue-categories" value={formData.category || ''} onChange={(e) => setFormData({ ...formData, category: e.target.value })} placeholder="Bearings, belts, hand tools..." className={fieldClass} /><datalist id="catalogue-categories">{categories.map((category) => <option key={category} value={category} />)}</datalist></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Manufacturer</label><input value={formData.manufacturer || ''} onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })} className={fieldClass} /></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Model number</label><input value={formData.model_number || ''} onChange={(e) => setFormData({ ...formData, model_number: e.target.value })} className={fieldClass} /></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Supplier</label><input value={formData.supplier || ''} onChange={(e) => setFormData({ ...formData, supplier: e.target.value })} className={fieldClass} /></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Location</label><input value={formData.location || ''} onChange={(e) => setFormData({ ...formData, location: e.target.value })} className={fieldClass} /></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Unit</label><input value={formData.unit_of_measure || ''} onChange={(e) => setFormData({ ...formData, unit_of_measure: e.target.value })} placeholder="pcs, set, box..." className={fieldClass} /></div>
            <div><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Unit cost</label><input type="number" min="0" step="0.01" value={formData.unit_cost ?? ''} onChange={(e) => setFormData({ ...formData, unit_cost: e.target.value ? Number(e.target.value) : undefined })} className={fieldClass} /></div>
            <div className="md:col-span-2"><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Compatible equipment</label><textarea rows={2} value={formData.compatible_equipment || ''} onChange={(e) => setFormData({ ...formData, compatible_equipment: e.target.value })} className={fieldClass} /></div>
            <div className="md:col-span-2"><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label><textarea rows={3} value={formData.description || ''} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className={fieldClass} /></div>
            <div className="md:col-span-2"><label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Notes</label><textarea rows={3} value={formData.notes || ''} onChange={(e) => setFormData({ ...formData, notes: e.target.value })} className={fieldClass} /></div>
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300"><input type="checkbox" checked={formData.is_active ?? true} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />Active catalogue item</label>
          </div>
        </section>

        <div className="flex justify-end gap-3">
          <button type="button" onClick={() => navigate('/maintenance/catalogue')} disabled={isSaving} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700">Cancel</button>
          <button type="submit" disabled={isSaving} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"><Save className="h-4 w-4" />{isSaving ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Item'}</button>
        </div>
      </form>
    </div>
  )
}

export default MaintenanceCatalogueFormPage
