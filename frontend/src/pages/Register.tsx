import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

export default function Register() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    username: '',
    email: '',
    password: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function handleChange(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!form.firstName || !form.lastName || !form.username || !form.email || !form.password) {
      setError('Please fill in all fields')
      return
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    const displayName = `${form.firstName.trim()} ${form.lastName.trim()}`.trim()
    setSubmitting(true)
    try {
      await register(form.email, form.password, displayName)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setSubmitting(false)
    }
  }

  const fields = [
    { key: 'firstName', label: 'First name:', type: 'text' },
    { key: 'lastName', label: 'Last name:', type: 'text' },
    { key: 'username', label: 'Username:', type: 'text' },
    { key: 'email', label: 'Email:', type: 'email' },
    { key: 'password', label: 'Password:', type: 'password' },
  ]

  return (
    <div className="max-w-md mx-auto px-6 py-16">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Register</h1>

      <form onSubmit={handleSubmit} className="space-y-5">
        {error && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-4 py-2">
            {error}
          </div>
        )}

        {fields.map((f) => (
          <div key={f.key}>
            <label className="block text-sm font-medium text-gray-700 mb-1">{f.label}</label>
            <input
              type={f.type}
              value={form[f.key as keyof typeof form]}
              onChange={(e) => handleChange(f.key, e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-400"
            />
          </div>
        ))}

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-2 bg-gray-900 text-white rounded-md font-medium hover:bg-gray-800 transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {submitting ? 'Creating account...' : 'Register'}
        </button>
      </form>

      <p className="mt-6 text-sm text-gray-500">
        Already have an account?{' '}
        <Link to="/login" className="text-blue-600 hover:underline">Login here</Link>
      </p>
    </div>
  )
}
