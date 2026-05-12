import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { fetchEventById } from '../api/events'
import { checkSaved, saveEvent, unsaveEvent } from '../api/saves'
import { useAuth } from '../context/useAuth'
import type { Event } from '../types/event'

function formatDate(datetime: string): string {
  return new Date(datetime).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatPrice(event: Event): string {
  if (event.is_free) return 'Free'
  if (event.price_min == null) return ''
  if (event.price_max != null && event.price_max !== event.price_min) {
    return `$${event.price_min}–$${event.price_max}`
  }
  return `$${event.price_min}`
}

export default function EventDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { token, isAuthenticated, isLoading: authLoading } = useAuth()
  const [event, setEvent] = useState<Event | null>(null)
  const [loading, setLoading] = useState(true)
  const [isSaved, setIsSaved] = useState(false)

  useEffect(() => {
    if (!id) return
    fetchEventById(id)
      .then(setEvent)
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (authLoading || !id) return
    if (!isAuthenticated || !token) {
      queueMicrotask(() => setIsSaved(false))
      return
    }
    checkSaved(token, id)
      .then(setIsSaved)
      .catch(() => setIsSaved(false))
  }, [authLoading, isAuthenticated, token, id])

  async function handleToggleSave() {
    if (!id) return
    if (!isAuthenticated || !token) {
      navigate('/login')
      return
    }
    const previous = isSaved
    setIsSaved(!previous)
    try {
      if (previous) await unsaveEvent(token, id)
      else await saveEvent(token, id)
    } catch {
      setIsSaved(previous)
    }
  }
  const handleExport = () => {
    window.location.href = `http://localhost:8000/api/export/${id}`
  }

  if (loading) {
    return <div className="max-w-3xl mx-auto px-6 py-12 text-center text-gray-400">Loading...</div>
  }

  if (!event) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-12 text-center">
        <p className="text-gray-500 mb-4">Event not found</p>
        <Link to="/" className="text-blue-600 hover:underline">Back to home</Link>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex gap-6 mb-6">
        <div className="flex-1">
          <div className="flex items-start justify-between gap-3 mb-2">
            <h1 className="text-2xl font-bold text-gray-900">{event.title}</h1>
            <button
              type="button"
              onClick={handleToggleSave}
              className="flex-shrink-0 p-1 hover:scale-110 transition-transform cursor-pointer bg-transparent border-none"
              aria-label={isSaved ? 'Unsave event' : 'Save event'}
            >
              <svg className="w-7 h-7" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                {isSaved ? (
                  <path fill="#ef4444" stroke="#ef4444" d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
                ) : (
                  <path fill="none" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                )}
              </svg>
            </button>
          </div>
          <p className="text-gray-600 mb-1">{formatDate(event.start_datetime)}</p>
          <p className="text-sm text-gray-500 mb-1">{event.source.replace('_', ' ')}</p>
          {event.source_url && (
            <a
              href={event.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:underline"
            >
              link to original posting
            </a>
          )}
        </div>

        {/* Image */}
        <div className="w-64 h-44 flex-shrink-0 rounded-lg overflow-hidden">
          {event.image_url ? (
            <img src={event.image_url} alt={event.title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gray-100 flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.41a2.25 2.25 0 013.182 0l2.909 2.91m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
              </svg>
            </div>
          )}
        </div>
      </div>

      {/* Description */}
      {event.description && (
        <div className="mb-8">
          <p className="text-gray-700 leading-relaxed">{event.description}</p>
        </div>
      )}

      {/* Location & actions */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold text-gray-900 mb-1">Location</h3>
          {event.venue_name && <p className="text-gray-700">{event.venue_name}</p>}
          {event.venue_address && <p className="text-sm text-gray-500">{event.venue_address}</p>}
        </div>
        <div className="text-right space-y-2">
          {formatPrice(event) && (
            <p className="font-semibold text-gray-900">{formatPrice(event)}</p>
          )}
          <button
            onClick={handleExport}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            📅 Add to Calendar
          </button>
        </div>
      </div>

      {/* Back link */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <Link to="/" className="text-sm text-blue-600 hover:underline">&larr; Back to events</Link>
      </div>
    </div>
  )
}
