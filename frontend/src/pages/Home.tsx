import { useEffect, useState } from 'react'
import EventCard from '../components/EventCard'
import { fetchEvents } from '../api/events'
import { getSavedIds, toggleSave } from '../utils/savedEvents'
import type { Event } from '../types/event'

export default function Home() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [savedIds, setSavedIds] = useState<Set<string>>(getSavedIds)

  useEffect(() => {
    fetchEvents()
      .then(setEvents)
      .finally(() => setLoading(false))
  }, [])

  function handleSaveToggle(id: string) {
    toggleSave(id)
    setSavedIds(getSavedIds())
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-6">
      {/* Location input — visible but non-functional */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="city / zip code"
          disabled
          className="px-4 py-2 border border-gray-200 rounded-md text-sm text-gray-400 bg-gray-50 cursor-not-allowed w-56"
        />
      </div>

      {/* Section header */}
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Explore</h2>

      {/* Event list */}
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
  )
}
