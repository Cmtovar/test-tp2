import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import EventCard from '../components/EventCard'
import { useAuth } from '../context/useAuth'
import { getSavedEvents, unsaveEvent } from '../api/saves'
import type { SavedEventEntry } from '../api/saves'

export default function MyEvents() {
  const { token, isAuthenticated, isLoading: authLoading } = useAuth()
  const [entries, setEntries] = useState<SavedEventEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated || !token) {
      queueMicrotask(() => setLoading(false))
      return
    }
    queueMicrotask(() => setLoading(true))
    getSavedEvents(token)
      .then((res) => setEntries(res.data))
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load saved events'))
      .finally(() => setLoading(false))
  }, [authLoading, isAuthenticated, token])

  async function handleUnsave(eventId: string) {
    if (!token) return
    const previous = entries
    setEntries((prev) => prev.filter((e) => e.event_id !== eventId))
    try {
      await unsaveEvent(token, eventId)
    } catch {
      setEntries(previous)
    }
  }

  if (authLoading || loading) {
    return <div className="max-w-5xl mx-auto px-6 py-12 text-center text-gray-400">Loading...</div>
  }

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto px-6 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Saved</h1>
        <p className="text-gray-600 mb-6">Please log in to see your saved events.</p>
        <Link
          to="/login"
          className="inline-block px-5 py-2 bg-gray-900 text-white rounded-md font-medium hover:bg-gray-800 transition-colors"
        >
          Log in
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Saved</h1>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-4 py-2 mb-4">
          {error}
        </div>
      )}

      {entries.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">
            No saved events yet. Browse events and tap the heart icon to save them.
          </p>
          <Link to="/" className="text-blue-600 hover:underline">Browse events</Link>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {entries.map((entry) => (
            <div
              key={entry.event_id}
            >
              <EventCard event={entry.event} isSaved onSaveToggle={handleUnsave} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
