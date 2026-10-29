import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ShieldCheck, Eye, EyeOff, AlertCircle, Loader2 } from 'lucide-react'

const DEMO_ACCOUNTS = [
  { label: 'Admin', email: 'admin@coalmine.gov', password: 'Admin@123', color: '#DC2626' },
  { label: 'Safety Officer', email: 'safety@coalmine.gov', password: 'Safety@123', color: '#D97706' },
  { label: 'Supervisor', email: 'supervisor@coalmine.gov', password: 'Super@123', color: '#2563EB' },
  { label: 'Worker', email: 'worker@coalmine.gov', password: 'Worker@123', color: '#16A34A' },
  { label: 'Auditor', email: 'auditor@coalmine.gov', password: 'Auditor@123', color: '#6B7280' },
]

export default function Login() {
  const [email, setEmail] = useState('admin@coalmine.gov')
  const [password, setPassword] = useState('Admin@123')
  const [showPwd, setShowPwd] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.detail || 'Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  function fillDemo(acc) {
    setEmail(acc.email)
    setPassword(acc.password)
    setError('')
  }

  return (
    <div className="min-h-screen bg-[#F7F8FA] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-[#1F2937] rounded-xl mb-4">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-[#1F2937] leading-tight">
            Coal Mine Safety<br />Governance System
          </h1>
          <p className="text-sm text-[#6B7280] mt-2">
            AI-Driven Digital Twin & Compliance Management
          </p>
          <span className="inline-block mt-2 px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded font-medium border border-blue-100">
            DGMS Compliant
          </span>
        </div>

        {/* Card */}
        <div className="bg-white border border-[#E5E7EB] rounded-lg p-6 shadow-sm">
          <h2 className="text-base font-semibold text-[#1F2937] mb-4">Sign in to your account</h2>

          {error && (
            <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 rounded-md p-3 mb-4 text-sm">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[#374151] mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="w-full px-3 py-2 border border-[#D1D5DB] rounded-md text-sm text-[#1F2937] bg-white placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="Enter your email"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[#374151] mb-1">Password</label>
              <div className="relative">
                <input
                  type={showPwd ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2 pr-10 border border-[#D1D5DB] rounded-md text-sm text-[#1F2937] bg-white placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#9CA3AF] hover:text-[#4B5563]"
                >
                  {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-[#2563EB] hover:bg-blue-700 text-white text-sm font-medium py-2.5 rounded-md transition disabled:opacity-60"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
        </div>

        {/* Demo Accounts */}
        <div className="bg-white border border-[#E5E7EB] rounded-lg p-4 mt-4 shadow-sm">
          <p className="text-xs font-semibold text-[#6B7280] uppercase tracking-wide mb-3">
            Demo Accounts — Click to fill
          </p>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {DEMO_ACCOUNTS.map(acc => (
              <button
                key={acc.label}
                onClick={() => fillDemo(acc)}
                className="text-left px-3 py-2 rounded-md border border-[#E5E7EB] hover:bg-[#F7F8FA] transition group"
              >
                <div className="flex items-center gap-1.5 mb-0.5">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: acc.color }}></div>
                  <span className="text-xs font-medium text-[#1F2937]">{acc.label}</span>
                </div>
                <p className="text-[10px] text-[#9CA3AF] truncate">{acc.email}</p>
              </button>
            ))}
          </div>
        </div>

        <p className="text-center text-xs text-[#9CA3AF] mt-6">
          B.Tech CSE (AI & ML) — Final Year Major Project<br />
          AI-Driven Digital Twin for Coal Mine Safety Governance
        </p>
      </div>
    </div>
  )
}
