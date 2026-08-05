import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Bell,
  CheckCheck,
  Trash2,
  Search,
  Settings,
  Package,
  Wrench,
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  Info,
  ExternalLink,
  Filter,
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { notificationService, type Notification, type NotificationType } from '../../services/notification.service'

const NotificationsPage = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'unread' | 'read'>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  useEffect(() => {
    loadNotifications()
  }, [])

  const loadNotifications = async () => {
    try {
      setLoading(true)
      const res = await notificationService.getNotifications({ limit: 100 })
      
      const userPermissions = user?.permissions || []
      const isAdmin = user?.role === 'admin'

      const filtered = res.data.filter((n) => {
        if (isAdmin) return true
        if (n.type === 'work_order') return userPermissions.includes('work_orders.view') || userPermissions.includes('*')
        if (n.type === 'inventory') return userPermissions.includes('inventory.view') || userPermissions.includes('*')
        if (n.type === 'maintenance') return userPermissions.includes('maintenance.view') || userPermissions.includes('*')
        if (n.type === 'quality') return userPermissions.includes('quality.view') || userPermissions.includes('*')
        if (['info', 'success', 'warning', 'error'].includes(n.type)) return true
        return false
      })

      setNotifications(filtered)
    } catch (err) {
      console.error('Failed to fetch notifications:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationService.markAsRead(id)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      )
    } catch (err) {
      console.error('Failed to mark notification as read:', err)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead()
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
    } catch (err) {
      console.error('Failed to mark all as read:', err)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await notificationService.deleteNotification(id)
      setNotifications((prev) => prev.filter((n) => n.id !== id))
    } catch (err) {
      console.error('Failed to delete notification:', err)
    }
  }

  const getNotificationIcon = (type: NotificationType) => {
    const iconClass = 'w-5 h-5'
    switch (type) {
      case 'work_order':
        return <Wrench className={`${iconClass} text-blue-500`} />
      case 'inventory':
        return <Package className={`${iconClass} text-yellow-500`} />
      case 'maintenance':
        return <Settings className={`${iconClass} text-orange-500`} />
      case 'quality':
        return <ShieldCheck className={`${iconClass} text-green-500`} />
      case 'success':
        return <CheckCircle className={`${iconClass} text-green-500`} />
      case 'warning':
        return <AlertTriangle className={`${iconClass} text-yellow-500`} />
      case 'error':
        return <AlertTriangle className={`${iconClass} text-red-500`} />
      default:
        return <Info className={`${iconClass} text-gray-500`} />
    }
  }

  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  const filteredNotifications = useMemo(() => {
    return notifications.filter((n) => {
      // Status filter
      if (statusFilter === 'unread' && n.read) return false
      if (statusFilter === 'read' && !n.read) return false

      // Category filter
      if (categoryFilter !== 'all' && n.type !== categoryFilter) return false

      // Search term filter
      if (searchTerm.trim() !== '') {
        const term = searchTerm.toLowerCase()
        const matchTitle = n.title.toLowerCase().includes(term)
        const matchMsg = n.message.toLowerCase().includes(term)
        if (!matchTitle && !matchMsg) return false
      }

      return true
    })
  }, [notifications, statusFilter, categoryFilter, searchTerm])

  const unreadCount = useMemo(() => {
    return notifications.filter((n) => !n.read).length
  }, [notifications])

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Notifications</h1>
            {unreadCount > 0 && (
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 rounded-full">
                {unreadCount} unread
              </span>
            )}
          </div>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
            View, filter, and manage all your facility system notifications
          </p>
        </div>

        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 shadow-sm transition-all"
          >
            <CheckCheck className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            Mark all as read
          </button>
        )}
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow dark:shadow-gray-900/50 p-4 border border-gray-100 dark:border-gray-700 space-y-4">
        <div className="flex flex-col md:flex-row gap-4 justify-between">
          {/* Search bar */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search notifications..."
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Read/Unread status tabs */}
          <div className="flex items-center bg-gray-100 dark:bg-gray-700 p-1 rounded-lg self-start">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                statusFilter === 'all'
                  ? 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              All ({notifications.length})
            </button>
            <button
              onClick={() => setStatusFilter('unread')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                statusFilter === 'unread'
                  ? 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              Unread ({unreadCount})
            </button>
            <button
              onClick={() => setStatusFilter('read')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                statusFilter === 'read'
                  ? 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              Read ({notifications.length - unreadCount})
            </button>
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-gray-100 dark:border-gray-700">
          <span className="text-xs font-medium text-gray-400 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {[
            { id: 'all', label: 'All Categories' },
            { id: 'work_order', label: 'Work Orders' },
            { id: 'inventory', label: 'Inventory' },
            { id: 'maintenance', label: 'Maintenance' },
            { id: 'quality', label: 'Quality' },
          ].map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategoryFilter(cat.id)}
              className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                categoryFilter === cat.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Notification List */}
      <div className="space-y-3">
        {loading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-100 dark:border-gray-700">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-500 text-sm mt-3">Loading notifications...</p>
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-100 dark:border-gray-700">
            <Bell className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-gray-700 dark:text-gray-300">No notifications found</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {searchTerm || statusFilter !== 'all' || categoryFilter !== 'all'
                ? 'Try adjusting your search or filters'
                : "You're all caught up!"}
            </p>
          </div>
        ) : (
          filteredNotifications.map((n) => (
            <div
              key={n.id}
              className={`bg-white dark:bg-gray-800 rounded-xl p-5 border transition-all shadow-sm ${
                !n.read
                  ? 'border-blue-200 dark:border-blue-900/50 bg-blue-50/30 dark:bg-blue-900/10'
                  : 'border-gray-100 dark:border-gray-700'
              }`}
            >
                <div className="flex items-start gap-3 sm:gap-4">
                <div className="p-2.5 rounded-lg bg-gray-50 dark:bg-gray-700 flex-shrink-0">
                  {getNotificationIcon(n.type)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-base font-semibold text-gray-800 dark:text-gray-100">{n.title}</h3>
                      {!n.read && (
                        <span className="px-2 py-0.5 text-xs font-semibold bg-blue-500 text-white rounded">
                          NEW
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">
                      {getRelativeTime(n.created_at)}
                    </span>
                  </div>

                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{n.message}</p>

                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mt-4 pt-3 border-t border-gray-100 dark:border-gray-700/60">
                    <div className="flex items-center gap-3">
                      {n.link && (
                        <button
                          onClick={() => navigate(n.link!)}
                          className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          View Details <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>

                    <div className="flex items-center gap-3">
                      {!n.read && (
                        <button
                          onClick={() => handleMarkAsRead(n.id)}
                          className="text-xs font-medium text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"
                        >
                          <CheckCheck className="w-3.5 h-3.5" /> Mark read
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(n.id)}
                        className="text-xs font-medium text-gray-400 hover:text-red-500 dark:hover:text-red-400 flex items-center gap-1 transition-colors"
                        title="Delete notification"
                      >
                        <Trash2 className="w-3.5 h-3.5" /> Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default NotificationsPage
