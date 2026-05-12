import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const location = useLocation()
  const { isAuthenticated, user } = useAuth()

  const profileLabel = isAuthenticated && user?.display_name ? user.display_name : 'Profile'
  const profilePath = isAuthenticated ? '/profile' : '/login'
  const profileText = isAuthenticated ? profileLabel : 'Login'

  const navItems = [
    { label: 'Home', path: '/' },
    { label: 'My Events', path: '/my-events' },
    { label: profileText, path: profilePath },
  ]

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <Link to="/" className="text-2xl font-bold text-gray-900 no-underline">
        ChiPulse
      </Link>
      <div className="flex gap-1">
        {navItems.map((item) => (
          <Link
            key={item.label}
            to={item.path}
            className={`px-4 py-2 rounded-md text-sm font-medium no-underline transition-colors ${
              location.pathname === item.path
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
