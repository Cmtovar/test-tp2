import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import EventCard from '../components/EventCard'
import { fetchEvents } from '../api/events'
import { getSavedEvents, saveEvent, unsaveEvent } from '../api/saves'
import { useAuth } from '../context/useAuth'
import type { Event } from '../types/event'

export default function Home() {
  const navigate = useNavigate()
  const { token, isAuthenticated, isLoading: authLoading } = useAuth()
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetchEvents()
      .then(setEvents)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated || !token) {
      queueMicrotask(() => setSavedIds(new Set()))
      return
    }
    getSavedEvents(token)
      .then((res) => setSavedIds(new Set(res.data.map((e) => e.event_id))))
      .catch(() => setSavedIds(new Set()))
  }, [authLoading, isAuthenticated, token])

  async function handleSaveToggle(id: string) {
    if (!isAuthenticated || !token) {
      navigate('/login')
      return
    }
    const isCurrentlySaved = savedIds.has(id)
    setSavedIds((prev) => {
      const next = new Set(prev)
      if (isCurrentlySaved) next.delete(id)
      else next.add(id)
      return next
    })
    try {
      if (isCurrentlySaved) await unsaveEvent(token, id)
      else await saveEvent(token, id)
    } catch {
      setSavedIds((prev) => {
        const next = new Set(prev)
        if (isCurrentlySaved) next.add(id)
        else next.delete(id)
        return next
      })
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-6">
      {/* Location input */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="city / zip code"
          disabled
          className="px-4 py-2 border border-gray-200 rounded-md text-sm text-gray-400 bg-gray-50 cursor-not-allowed w-56"
        />
      </div>

      {/* Section header tabs */}
      <div className="flex gap-4 mb-6">
        <button className="text-lg font-semibold text-gray-900 border-b-2 border-gray-900 pb-1 cursor-default">
          Explore
        </button>
        <button className="text-lg font-semibold text-gray-400 pb-1 cursor-default">
          Recommended
        </button>
      </div>

      <div className="flex gap-8">
        {/* Filter sidebar */}
        <aside className="w-48 flex-shrink-0">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Filters</h3>
          <div className="space-y-4">
            {[
              { label: '$', value: 'Any price' },
              { label: 'Distance', value: 'Any distance' },
              { label: 'Date', value: 'Any date' },
              { label: 'Category', value: 'All categories' },
            ].map((f) => (
              <div key={f.label}>
                <label className="block text-sm text-gray-600 mb-1">{f.label}</label>
                <div className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-400 cursor-not-allowed">
                  {f.value}
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-4">No filtering applied</p>
        </aside>

        {/* Event list */}
        <div className="flex-1">
          {loading ? (
            <div className="text-center py-12 text-gray-400">Loading events...</div>
          ) : events.length === 0 ? (
            <div className="text-center py-12 text-gray-400">No events found</div>
          ) : (
            <div className="flex flex-col gap-4">
              {events.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  isSaved={savedIds.has(event.id)}
                  onSaveToggle={handleSaveToggle}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
