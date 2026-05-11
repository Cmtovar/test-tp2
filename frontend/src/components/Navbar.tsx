import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import Toast from './Toast'

const navItems = [
  { label: 'Home', path: '/', implemented: true },
  { label: 'My Events', path: '/my-events', implemented: false },
  { label: 'Profile', path: '/login', implemented: true },
]

export default function Navbar() {
  const location = useLocation()
  const [toast, setToast] = useState<string | null>(null)

  function handleNavClick(e: React.MouseEvent, item: (typeof navItems)[0]) {
    if (!item.implemented) {
      e.preventDefault()
      setToast(`${item.label} — coming soon`)
    }
  }

  return (
    <>
      <Toast message={toast} onClose={() => setToast(null)} />
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold text-gray-900 no-underline">
          ChiPulse
        </Link>
        <div className="flex gap-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={(e) => handleNavClick(e, item)}
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
    </>
  )
}
