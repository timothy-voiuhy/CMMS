/**
 * Permission Editor Component
 * Full UI for configuring role permissions with category grouping,
 * template selection, search, and implied permission indicators.
 */

import { useState, useEffect, useMemo, useCallback } from 'react'
import { Search, ChevronDown, ChevronRight, Zap, Info, Check, X, RotateCcw } from 'lucide-react'
import { PERMISSION_REGISTRY, ROLE_TEMPLATES, CATEGORY_ORDER, resolvePermissions } from '../../config/permissions'

interface PermissionEditorProps {
  /** Currently granted (raw) permissions */
  permissions: string[]
  /** Callback when permissions change */
  onChange: (permissions: string[]) => void
  /** Whether the editor is read-only */
  readOnly?: boolean
}

// Category icons/colors for visual distinction
const CATEGORY_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  'Dashboard': { bg: 'bg-sky-50 dark:bg-sky-900/20', text: 'text-sky-700 dark:text-sky-400', border: 'border-sky-200 dark:border-sky-800' },
  'Equipment': { bg: 'bg-orange-50 dark:bg-orange-900/20', text: 'text-orange-700 dark:text-orange-400', border: 'border-orange-200 dark:border-orange-800' },
  'Inventory': { bg: 'bg-emerald-50 dark:bg-emerald-900/20', text: 'text-emerald-700 dark:text-emerald-400', border: 'border-emerald-200 dark:border-emerald-800' },
  'Production': { bg: 'bg-violet-50 dark:bg-violet-900/20', text: 'text-violet-700 dark:text-violet-400', border: 'border-violet-200 dark:border-violet-800' },
  'Quality': { bg: 'bg-rose-50 dark:bg-rose-900/20', text: 'text-rose-700 dark:text-rose-400', border: 'border-rose-200 dark:border-rose-800' },
  'Maintenance': { bg: 'bg-amber-50 dark:bg-amber-900/20', text: 'text-amber-700 dark:text-amber-400', border: 'border-amber-200 dark:border-amber-800' },
  'Work Orders': { bg: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-700 dark:text-blue-400', border: 'border-blue-200 dark:border-blue-800' },
  'Personnel': { bg: 'bg-teal-50 dark:bg-teal-900/20', text: 'text-teal-700 dark:text-teal-400', border: 'border-teal-200 dark:border-teal-800' },
  'Reports': { bg: 'bg-indigo-50 dark:bg-indigo-900/20', text: 'text-indigo-700 dark:text-indigo-400', border: 'border-indigo-200 dark:border-indigo-800' },
  'Settings': { bg: 'bg-gray-50 dark:bg-gray-800/50', text: 'text-gray-700 dark:text-gray-400', border: 'border-gray-200 dark:border-gray-700' },
  'Administration': { bg: 'bg-red-50 dark:bg-red-900/20', text: 'text-red-700 dark:text-red-400', border: 'border-red-200 dark:border-red-800' },
}

const PermissionEditor = ({ permissions, onChange, readOnly = false }: PermissionEditorProps) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(CATEGORY_ORDER))
  const [showTemplates, setShowTemplates] = useState(false)

  // Group permissions by category
  const groupedPermissions = useMemo(() => {
    const grouped: Record<string, { key: string; name: string; description: string; implies: string[] }[]> = {}

    for (const [key, def] of Object.entries(PERMISSION_REGISTRY)) {
      // Skip the wildcard-implying admin permission from individual toggles display
      if (key === 'admin.full_access') continue

      if (!grouped[def.category]) {
        grouped[def.category] = []
      }
      grouped[def.category].push({
        key,
        name: def.name,
        description: def.description,
        implies: def.implies,
      })
    }

    return grouped
  }, [])

  // Resolve effective permissions (what the user actually gets)
  const resolvedPermissions = useMemo(() => {
    return new Set(resolvePermissions(permissions))
  }, [permissions])

  // Check if a permission is explicitly granted (not just implied)
  const isExplicitlyGranted = useCallback((permKey: string) => {
    return permissions.includes(permKey)
  }, [permissions])

  // Check if a permission is implied by another granted permission
  const isImplied = useCallback((permKey: string) => {
    return resolvedPermissions.has(permKey) && !permissions.includes(permKey)
  }, [resolvedPermissions, permissions])

  // Check for full access
  const hasFullAccess = useMemo(() => {
    return permissions.includes('admin.full_access') || permissions.includes('*')
  }, [permissions])

  // Filter by search
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return CATEGORY_ORDER.filter((c) => groupedPermissions[c])

    const query = searchQuery.toLowerCase()
    return CATEGORY_ORDER.filter((category) => {
      const perms = groupedPermissions[category]
      if (!perms) return false
      return (
        category.toLowerCase().includes(query) ||
        perms.some(
          (p) =>
            p.key.toLowerCase().includes(query) ||
            p.name.toLowerCase().includes(query) ||
            p.description.toLowerCase().includes(query)
        )
      )
    })
  }, [searchQuery, groupedPermissions])

  // Toggle a single permission
  const togglePermission = (permKey: string) => {
    if (readOnly) return

    if (permissions.includes(permKey)) {
      // Remove it
      onChange(permissions.filter((p) => p !== permKey))
    } else {
      // Add it
      onChange([...permissions, permKey])
    }
  }

  // Toggle all permissions in a category
  const toggleCategory = (category: string) => {
    if (readOnly) return

    const categoryPerms = groupedPermissions[category]
    if (!categoryPerms) return

    const categoryKeys = categoryPerms.map((p) => p.key)
    const allGranted = categoryKeys.every((k) => permissions.includes(k))

    if (allGranted) {
      // Remove all category permissions
      onChange(permissions.filter((p) => !categoryKeys.includes(p)))
    } else {
      // Add all missing category permissions
      const newPerms = new Set(permissions)
      categoryKeys.forEach((k) => newPerms.add(k))
      onChange([...newPerms])
    }
  }

  // Toggle expand/collapse category
  const toggleExpand = (category: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  // Toggle full admin access
  const toggleFullAccess = () => {
    if (readOnly) return

    if (hasFullAccess) {
      onChange(permissions.filter((p) => p !== 'admin.full_access' && p !== '*'))
    } else {
      onChange(['admin.full_access'])
    }
  }

  // Apply a template
  const applyTemplate = (templateKey: string) => {
    if (readOnly) return

    const template = ROLE_TEMPLATES[templateKey]
    if (template) {
      onChange([...template.permissions])
      setShowTemplates(false)
    }
  }

  // Clear all permissions
  const clearAll = () => {
    if (readOnly) return
    onChange([])
  }

  // Count granted permissions per category
  const getCategoryCount = (category: string) => {
    const categoryPerms = groupedPermissions[category]
    if (!categoryPerms) return { granted: 0, total: 0 }

    const total = categoryPerms.length
    const granted = categoryPerms.filter((p) => resolvedPermissions.has(p.key)).length
    return { granted, total }
  }

  return (
    <div className="space-y-4">
      {/* Full Access Toggle */}
      <div className={`p-4 rounded-lg border-2 transition-all ${
        hasFullAccess
          ? 'border-red-400 dark:border-red-600 bg-red-50 dark:bg-red-900/20'
          : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className={`w-5 h-5 ${hasFullAccess ? 'text-red-500' : 'text-gray-400'}`} />
            <div>
              <p className="font-semibold text-gray-900 dark:text-gray-100">Full System Access</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Grants complete access to all system features
              </p>
            </div>
          </div>
          <button
            onClick={toggleFullAccess}
            disabled={readOnly}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              hasFullAccess ? 'bg-red-500' : 'bg-gray-300 dark:bg-gray-600'
            } ${readOnly ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                hasFullAccess ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Toolbar */}
      {!hasFullAccess && (
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search permissions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
            />
          </div>

          {/* Template Selector */}
          <div className="relative">
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              disabled={readOnly}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-200 disabled:opacity-50 whitespace-nowrap"
            >
              <Zap className="w-4 h-4" />
              Apply Template
              <ChevronDown className="w-3 h-3" />
            </button>

            {showTemplates && (
              <div className="absolute right-0 top-full mt-1 w-72 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto">
                {Object.entries(ROLE_TEMPLATES).map(([key, template]) => (
                  <button
                    key={key}
                    onClick={() => applyTemplate(key)}
                    className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm text-gray-900 dark:text-gray-100">
                        {template.name}
                      </span>
                      <span className="text-xs px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded-full">
                        L{template.level}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                      {template.description}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Clear All */}
          <button
            onClick={clearAll}
            disabled={readOnly || permissions.length === 0}
            className="flex items-center gap-1 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg disabled:opacity-50 whitespace-nowrap"
          >
            <RotateCcw className="w-3 h-3" />
            Clear
          </button>
        </div>
      )}

      {/* Permission summary */}
      <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 px-1">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-blue-500 inline-block"></span>
          {resolvedPermissions.size} effective
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-green-500 inline-block"></span>
          {permissions.length} explicit
        </span>
        {resolvedPermissions.size > permissions.length && (
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded bg-yellow-500 inline-block"></span>
            {resolvedPermissions.size - permissions.length} inherited
          </span>
        )}
      </div>

      {/* Permission Categories */}
      {!hasFullAccess && (
        <div className="space-y-2">
          {filteredCategories.map((category) => {
            const categoryPerms = groupedPermissions[category]
            if (!categoryPerms) return null

            const isExpanded = expandedCategories.has(category)
            const { granted, total } = getCategoryCount(category)
            const style = CATEGORY_STYLES[category] || CATEGORY_STYLES['Settings']

            // Filter permissions by search
            const filteredPerms = searchQuery.trim()
              ? categoryPerms.filter(
                  (p) =>
                    p.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    p.description.toLowerCase().includes(searchQuery.toLowerCase())
                )
              : categoryPerms

            if (filteredPerms.length === 0) return null

            return (
              <div
                key={category}
                className={`border rounded-lg overflow-hidden ${style.border}`}
              >
                {/* Category Header */}
                <div
                  className={`flex items-center justify-between px-4 py-3 cursor-pointer select-none ${style.bg}`}
                  onClick={() => toggleExpand(category)}
                >
                  <div className="flex items-center gap-3">
                    {isExpanded ? (
                      <ChevronDown className={`w-4 h-4 ${style.text}`} />
                    ) : (
                      <ChevronRight className={`w-4 h-4 ${style.text}`} />
                    )}
                    <span className={`font-semibold text-sm ${style.text}`}>{category}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {granted}/{total}
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleCategory(category)
                    }}
                    disabled={readOnly}
                    className="text-xs px-2 py-1 rounded hover:bg-white/50 dark:hover:bg-gray-700/50 text-gray-600 dark:text-gray-400 disabled:opacity-50"
                  >
                    {granted === total ? 'Deselect All' : 'Select All'}
                  </button>
                </div>

                {/* Permission Items */}
                {isExpanded && (
                  <div className="divide-y divide-gray-100 dark:divide-gray-700/50">
                    {filteredPerms.map((perm) => {
                      const explicit = isExplicitlyGranted(perm.key)
                      const implied = isImplied(perm.key)
                      const active = explicit || implied

                      return (
                        <div
                          key={perm.key}
                          className={`flex items-center justify-between px-4 py-2.5 transition-colors ${
                            active
                              ? 'bg-blue-50/50 dark:bg-blue-900/10'
                              : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750'
                          }`}
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                {perm.name}
                              </span>
                              {implied && (
                                <span className="text-xs px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400">
                                  inherited
                                </span>
                              )}
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                              {perm.description}
                            </p>
                            <code className="text-xs text-gray-400 dark:text-gray-500 font-mono">
                              {perm.key}
                            </code>
                          </div>
                          <button
                            onClick={() => togglePermission(perm.key)}
                            disabled={readOnly || implied}
                            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors flex-shrink-0 ml-3 ${
                              active
                                ? implied
                                  ? 'bg-yellow-400 dark:bg-yellow-600'
                                  : 'bg-blue-500 dark:bg-blue-600'
                                : 'bg-gray-300 dark:bg-gray-600'
                            } ${readOnly || implied ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
                          >
                            <span
                              className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                                active ? 'translate-x-4.5' : 'translate-x-0.5'
                              }`}
                              style={{ transform: active ? 'translateX(17px)' : 'translateX(2px)' }}
                            />
                          </button>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Full access message */}
      {hasFullAccess && (
        <div className="text-center py-8">
          <Zap className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <p className="text-lg font-medium text-gray-900 dark:text-gray-100">Full Access Enabled</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            This role has access to all {Object.keys(PERMISSION_REGISTRY).length} permissions in the system.
          </p>
        </div>
      )}

      {/* Click outside handler for template dropdown */}
      {showTemplates && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowTemplates(false)}
        />
      )}
    </div>
  )
}

export default PermissionEditor
