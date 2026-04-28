import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchEventById } from '../api/events'
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
  const [event, setEvent] = useState<Event | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    fetchEventById(id)
      .then(setEvent)
      .finally(() => setLoading(false))
  }, [id])

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
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{event.title}</h1>
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
        <div className="text-right">
          {formatPrice(event) && (
            <p className="font-semibold text-gray-900">{formatPrice(event)}</p>
          )}
        </div>
      </div>

      {/* Back link */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <Link to="/" className="text-sm text-blue-600 hover:underline">&larr; Back to events</Link>
      </div>
    </div>
  )
}
