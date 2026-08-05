import { useMemo, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  AlertTriangle,
  CheckCircle2,
  Eye,
  KeyRound,
  Loader2,
  LogIn,
  ShieldCheck,
  UserCheck,
  Users,
} from 'lucide-react'
import { authService } from '../../services/auth.service'
import { useAuthStore, type User as AuthStoreUser } from '../../store/authStore'

interface Persona {
  label: string
  username: string
  password: string
  role: string
  department: string
  summary: string
  visibleAreas: string[]
}

const PERSONAS: Persona[] = [
  {
    label: 'System Administrator',
    username: 'admin',
    password: 'admin123',
    role: 'Admin',
    department: 'System',
    summary: 'Full access for checking every module, settings page, and permission-controlled action.',
    visibleAreas: ['Everything', 'Settings', 'Role management', 'All reports'],
  },
  {
    label: 'General Manager',
    username: 'gmukasa',
    password: 'gm123',
    role: 'General Manager',
    department: 'Management',
    summary: 'Executive view with broad access across operations, reports, and approvals.',
    visibleAreas: ['Everything', 'Reports', 'Sales', 'Production'],
  },
  {
    label: 'Production Manager',
    username: 'lwaswa',
    password: 'prod123',
    role: 'Production Manager',
    department: 'Production',
    summary: 'Production leadership view for production orders, lines, equipment, and related reports.',
    visibleAreas: ['Production', 'Equipment', 'Inventory', 'Reports'],
  },
  {
    label: 'Maintenance Manager',
    username: 'mbabazi',
    password: 'maint123',
    role: 'Maintenance Manager',
    department: 'Maintenance',
    summary: 'Maintenance leadership view for work orders, equipment, technicians, and parts/tools.',
    visibleAreas: ['Maintenance', 'Work Orders', 'Equipment', 'Parts & Tools'],
  },
  {
    label: 'Quality Manager',
    username: 'nakyeyune',
    password: 'quality123',
    role: 'Quality Manager',
    department: 'Quality Control',
    summary: 'Quality management view for inspections, NCRs, production visibility, and quality reports.',
    visibleAreas: ['Quality', 'Production', 'Inventory', 'Reports'],
  },
  {
    label: 'Sales Manager',
    username: 'sserwanga',
    password: 'sales123',
    role: 'Sales Manager',
    department: 'Sales',
    summary: 'Sales leadership view for customers, orders, fulfillment coordination, and sales reporting.',
    visibleAreas: ['Sales', 'Customers', 'Orders', 'Reports'],
  },
  {
    label: 'Sales Representative',
    username: 'akeru',
    password: 'salesrep123',
    role: 'Sales Representative',
    department: 'Sales',
    summary: 'Sales desk view for customer records and draft sales order entry.',
    visibleAreas: ['Sales', 'Customers', 'Draft Orders', 'Inventory view'],
  },
  {
    label: 'Inventory Clerk',
    username: 'pkato',
    password: 'inv123',
    role: 'Inventory Clerk',
    department: 'Warehouse',
    summary: 'Warehouse view for stock, categories, transactions, and inventory reports.',
    visibleAreas: ['Inventory', 'Transactions', 'Production view', 'Reports'],
  },
  {
    label: 'Dispatch Clerk',
    username: 'kisembo',
    password: 'dispatch123',
    role: 'Dispatch Clerk',
    department: 'Dispatch',
    summary: 'Dispatch view for confirmed sales orders and issuing finished goods stock.',
    visibleAreas: ['Sales orders', 'Fulfillment', 'Inventory view', 'Sales reports'],
  },
  {
    label: 'Maintenance Team Leader',
    username: 'nnamutebi',
    password: 'craft123',
    role: 'Maintenance Team Leader',
    department: 'Maintenance',
    summary: 'Supervisor view for work order completion, catalogue upkeep, and assigned maintenance activity.',
    visibleAreas: ['Maintenance', 'Work Orders', 'Parts & Tools', 'Equipment'],
  },
  {
    label: 'Technician',
    username: 'okello',
    password: 'craft123',
    role: 'Technician',
    department: 'Utilities',
    summary: 'Hands-on technician view for work orders, maintenance completion, and equipment lookup.',
    visibleAreas: ['Work Orders', 'Maintenance', 'Equipment', 'Inventory view'],
  },
  {
    label: 'Machine Operator',
    username: 'akello',
    password: 'craft123',
    role: 'Machine Operator',
    department: 'Production',
    summary: 'Operator view for production execution, equipment visibility, and basic material requests.',
    visibleAreas: ['Production', 'Equipment', 'Quality view', 'Requisitions'],
  },
]

const toAuthStoreRole = (role?: string): AuthStoreUser['role'] => {
  const normalized = (role || 'readonly').toLowerCase()
  const allowedRoles: AuthStoreUser['role'][] = ['admin', 'craftsman', 'inventory', 'production', 'quality', 'manager', 'readonly']
  return allowedRoles.includes(normalized as AuthStoreUser['role'])
    ? normalized as AuthStoreUser['role']
    : 'readonly'
}

const RoleTestingPage = () => {
  const navigate = useNavigate()
  const { user, login, logout } = useAuthStore()
  const [activeUsername, setActiveUsername] = useState<string | null>(null)
  const [error, setError] = useState('')

  const groupedPersonas = useMemo(() => {
    return PERSONAS.reduce<Record<string, Persona[]>>((groups, persona) => {
      groups[persona.department] = groups[persona.department] || []
      groups[persona.department].push(persona)
      return groups
    }, {})
  }, [])

  const signInAs = async (persona: Persona) => {
    setError('')
    setActiveUsername(persona.username)

    try {
      const response = await authService.login({
        username: persona.username,
        password: persona.password,
      })

      const tempUser = {
        id: '0',
        username: persona.username,
        full_name: persona.label,
        email: '',
        role: 'readonly' as const,
        is_active: true,
        created_at: '',
        updated_at: '',
        permissions: [],
      }

      login(tempUser, response.access_token, response.refresh_token)
      const currentUser = await authService.getCurrentUser()

      login(
        {
          id: currentUser.id.toString(),
          username: currentUser.username,
          full_name: currentUser.full_name,
          email: currentUser.email,
          role: toAuthStoreRole(currentUser.role),
          is_active: currentUser.is_active,
          phone: currentUser.phone,
          created_at: currentUser.created_at || '',
          updated_at: currentUser.updated_at || '',
          permissions: currentUser.permissions || [],
        },
        response.access_token,
        response.refresh_token
      )

      navigate('/dashboard')
    } catch (err: unknown) {
      logout()
      const detail = typeof err === 'object' && err !== null && 'response' in err
        ? (err as { response?: { data?: { detail?: unknown } } }).response?.data?.detail
        : undefined
      setError(typeof detail === 'string' ? detail : 'Unable to sign in with that development account.')
    } finally {
      setActiveUsername(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div>
            <div className="flex items-center gap-2 text-sm font-medium text-amber-700 dark:text-amber-300">
              <AlertTriangle className="h-4 w-4" />
              Development testing only
            </div>
            <h1 className="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">
              Role Perspective Sign-In
            </h1>
            <p className="mt-1 max-w-3xl text-sm text-gray-600 dark:text-gray-300">
              Use this page on seeded development databases to sign in as predefined users and verify
              how navigation, pages, and actions change for each role. Each button performs a real
              login using the demo credentials shown on the card.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Link
              to="/login"
              className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
            >
              <KeyRound className="h-4 w-4" />
              Standard Login
            </Link>
            {user && (
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-3 py-2 text-sm font-medium text-white hover:bg-primary-700"
              >
                <Eye className="h-4 w-4" />
                View Current Session
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {user && (
          <div className="mb-5 flex flex-col gap-3 rounded-lg border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-900/70 dark:bg-emerald-950/30 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="mt-0.5 h-5 w-5 flex-shrink-0 text-emerald-600 dark:text-emerald-300" />
              <div>
                <p className="text-sm font-semibold text-emerald-900 dark:text-emerald-100">
                  Current session: {user.full_name || user.username}
                </p>
                <p className="text-sm text-emerald-800 dark:text-emerald-200">
                  Username `{user.username}`, base role `{user.role}`, {user.permissions?.length || 0} effective permissions loaded.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => {
                logout()
                navigate('/dev/role-testing')
              }}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-emerald-300 px-3 py-2 text-sm font-medium text-emerald-900 hover:bg-emerald-100 dark:border-emerald-700 dark:text-emerald-100 dark:hover:bg-emerald-900/40"
            >
              Clear Session
            </button>
          </div>
        )}

        {error && (
          <div className="mb-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/70 dark:bg-red-950/30 dark:text-red-200">
            {error}
          </div>
        )}

        <section className="mb-6 grid gap-4 lg:grid-cols-3">
          <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
            <div className="flex items-center gap-3">
              <ShieldCheck className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">What To Check</h2>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
              Confirm that the sidebar only shows allowed modules and restricted action buttons disappear or return permission errors.
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
            <div className="flex items-center gap-3">
              <UserCheck className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">How Switching Works</h2>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
              Choosing a persona replaces the current browser session with that account and opens the dashboard immediately.
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
            <div className="flex items-center gap-3">
              <Users className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Seed Dependency</h2>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
              These accounts are created by `scripts/seed_data.py`; reseed the database if a listed login fails.
            </p>
          </div>
        </section>

        <div className="space-y-6">
          {Object.entries(groupedPersonas).map(([department, personas]) => (
            <section key={department}>
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                {department}
              </h2>
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {personas.map((persona) => {
                  const loading = activeUsername === persona.username

                  return (
                    <article
                      key={persona.username}
                      className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
                            {persona.label}
                          </h3>
                          <p className="mt-1 text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                            {persona.role}
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => signInAs(persona)}
                          disabled={Boolean(activeUsername)}
                          className="inline-flex flex-shrink-0 items-center justify-center gap-2 rounded-lg bg-primary-600 px-3 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogIn className="h-4 w-4" />}
                          Sign In
                        </button>
                      </div>

                      <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">{persona.summary}</p>

                      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <dt className="text-xs font-medium uppercase text-gray-500 dark:text-gray-400">Username</dt>
                          <dd className="mt-1 font-mono text-gray-900 dark:text-gray-100">{persona.username}</dd>
                        </div>
                        <div>
                          <dt className="text-xs font-medium uppercase text-gray-500 dark:text-gray-400">Password</dt>
                          <dd className="mt-1 font-mono text-gray-900 dark:text-gray-100">{persona.password}</dd>
                        </div>
                      </dl>

                      <div className="mt-4 flex flex-wrap gap-2">
                        {persona.visibleAreas.map((area) => (
                          <span
                            key={area}
                            className="rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-200"
                          >
                            {area}
                          </span>
                        ))}
                      </div>
                    </article>
                  )
                })}
              </div>
            </section>
          ))}
        </div>
      </main>
    </div>
  )
}

export default RoleTestingPage
