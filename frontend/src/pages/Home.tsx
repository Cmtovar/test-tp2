import { useEffect, useState } from 'react'
import EventCard from '../components/EventCard'
import { fetchEvents } from '../api/events'
import type { Event } from '../types/event'

export default function Home() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchEvents()
      .then(setEvents)
      .finally(() => setLoading(false))
  }, [])

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
            <div>
              <label className="block text-sm text-gray-600 mb-1">$</label>
              <select disabled className="w-full px-2 py-1.5 border border-gray-200 rounded-md text-sm text-gray-400 bg-gray-50 cursor-not-allowed">
                <option>Any price</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Distance</label>
              <select disabled className="w-full px-2 py-1.5 border border-gray-200 rounded-md text-sm text-gray-400 bg-gray-50 cursor-not-allowed">
                <option>Any distance</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Date</label>
              <select disabled className="w-full px-2 py-1.5 border border-gray-200 rounded-md text-sm text-gray-400 bg-gray-50 cursor-not-allowed">
                <option>Any date</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Category</label>
              <select disabled className="w-full px-2 py-1.5 border border-gray-200 rounded-md text-sm text-gray-400 bg-gray-50 cursor-not-allowed">
                <option>All categories</option>
              </select>
            </div>
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
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
