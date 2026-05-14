import { useEffect, useState, useCallback } from 'react'
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

  // Filter state
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [isFree, setIsFree] = useState(false)
  const [priceMin, setPriceMin] = useState('')
  const [priceMax, setPriceMax] = useState('')

  const loadEvents = useCallback(() => {
    setLoading(true)
    const params: Record<string, string> = {}
    if (search) params.q = search
    if (category) params.category = category
    if (dateFrom) {
      params.date_from = dateFrom
      params.date_to = dateFrom
    }
    if (isFree) params.is_free = 'true'
    if (priceMin) params.price_min = priceMin
    if (priceMax) params.price_max = priceMax
    fetchEvents(params)
      .then(setEvents)
      .finally(() => setLoading(false))
  }, [search, category, dateFrom, isFree, priceMin, priceMax])

  useEffect(() => {
    loadEvents()
  }, [loadEvents])

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated || !token) {
      setSavedIds(new Set())
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

  const hasFilters = search || category || dateFrom || isFree || priceMin || priceMax

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

      {/* Search bar */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search events..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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

            {/* Price range */}
            <div>
              <label className="block text-sm text-gray-600 mb-1">Price range</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  min="0"
                  placeholder="Min"
                  value={priceMin}
                  onChange={(e) => setPriceMin(e.target.value)}
                  className="w-1/2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  min="0"
                  placeholder="Max"
                  value={priceMax}
                  onChange={(e) => setPriceMax(e.target.value)}
                  className="w-1/2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Free only toggle */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="isFree"
                checked={isFree}
                onChange={(e) => setIsFree(e.target.checked)}
                className="w-4 h-4 accent-blue-600"
              />
              <label htmlFor="isFree" className="text-sm text-gray-600 cursor-pointer">
                Free events only
              </label>
            </div>

            {/* Date */}
            <div>
              <label className="block text-sm text-gray-600 mb-1">Date</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm text-gray-600 mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All categories</option>
                <option value="music">Music</option>
                <option value="sports">Sports</option>
                <option value="theater">Theater</option>
                <option value="community">Community</option>
                <option value="food">Food</option>
                <option value="arts">Arts</option>
                <option value="family">Family</option>
              </select>
            </div>

            {/* Clear filters */}
            {hasFilters && (
              <button
                onClick={() => {
                  setSearch('')
                  setCategory('')
                  setDateFrom('')
                  setIsFree(false)
                  setPriceMin('')
                  setPriceMax('')
                }}
                className="text-xs text-blue-600 hover:underline"
              >
                Clear all filters
              </button>
            )}

          </div>
          <p className="text-xs text-gray-400 mt-4">
            {hasFilters ? 'Filters active' : 'No filtering applied'}
          </p>
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
