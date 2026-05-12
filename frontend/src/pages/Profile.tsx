import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

export default function Profile() {
  const navigate = useNavigate()
  const { user, isAuthenticated, isLoading, logout } = useAuth()

  if (isLoading) {
    return (
      <div className="max-w-md mx-auto px-6 py-16 text-center text-gray-400">Loading...</div>
    )
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="max-w-md mx-auto px-6 py-16">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Profile</h1>
        <p className="text-gray-600 mb-8">Sign in to save events and manage your profile</p>
        <div className="space-y-3">
          <Link
            to="/register"
            className="block w-full py-2 bg-gray-900 text-white rounded-md font-medium text-center hover:bg-gray-800 transition-colors"
          >
            Register here
          </Link>
          <Link
            to="/login"
            className="block w-full py-2 bg-white border border-gray-300 text-gray-900 rounded-md font-medium text-center hover:bg-gray-50 transition-colors"
          >
            Login here
          </Link>
        </div>
      </div>
    )
  }

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Profile</h1>

      <div className="flex gap-8">
        {/* Sidebar */}
        <aside className="w-40 flex-shrink-0">
          <nav className="space-y-1">
            <span className="block px-3 py-2 text-sm font-medium text-gray-900 bg-gray-100 rounded-md">
              My Info
            </span>
            <span className="block px-3 py-2 text-sm text-gray-500 cursor-default">
              Past Events
            </span>
          </nav>
        </aside>

        {/* My Info section */}
        <section className="flex-1 max-w-md">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">My Info</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={user.display_name ?? ''}
                readOnly
                className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={user.email}
                readOnly
                className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
              />
            </div>

            <p className="text-sm text-gray-400 italic">Other info...</p>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="mt-8 px-5 py-2 bg-gray-900 text-white rounded-md font-medium hover:bg-gray-800 transition-colors cursor-pointer"
          >
            Log out
          </button>
        </section>
      </div>
    </div>
  )
}
