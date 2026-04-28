import { Link } from 'react-router-dom'
import type { EventCardProps } from '../types/event'

function formatPrice(event: EventCardProps['event']): string {
  if (event.is_free) return 'Free'
  if (event.price_min == null) return ''
  if (event.price_max != null && event.price_max !== event.price_min) {
    return `$${event.price_min}–$${event.price_max}`
  }
  return `$${event.price_min}`
}

function formatDate(datetime: string): string {
  return new Date(datetime).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export default function EventCard({ event, isSaved = false, onSaveToggle }: EventCardProps) {
  const price = formatPrice(event)

  return (
    <Link
      to={`/events/${event.id}`}
      className="block no-underline text-inherit bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow overflow-hidden"
    >
      <div className="flex">
        {/* Image */}
        <div className="w-48 min-h-36 flex-shrink-0 relative">
          {event.image_url ? (
            <img
              src={event.image_url}
              alt={event.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gray-100 flex items-center justify-center">
              <svg className="w-10 h-10 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.41a2.25 2.25 0 013.182 0l2.909 2.91m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
              </svg>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 p-4 flex flex-col justify-between min-w-0">
          <div className="flex justify-between items-start gap-2">
            <div className="min-w-0">
              <h3 className="font-semibold text-gray-900 text-base truncate">{event.title}</h3>
              {event.description && (
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">{event.description}</p>
              )}
            </div>

            {/* Heart icon */}
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                onSaveToggle?.(event.id)
              }}
              className="flex-shrink-0 p-1 hover:scale-110 transition-transform cursor-pointer bg-transparent border-none"
              aria-label={isSaved ? 'Unsave event' : 'Save event'}
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                {isSaved ? (
                  <path fill="#ef4444" stroke="#ef4444" d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
                ) : (
                  <path fill="none" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                )}
              </svg>
            </button>
          </div>

          {/* Meta row */}
          <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
            <span>{formatDate(event.start_datetime)}</span>
            {event.neighborhood && <span>{event.neighborhood}</span>}
            {price && <span className="font-medium text-gray-700">{price}</span>}
          </div>
        </div>
      </div>

      {/* Source attribution */}
      <div className="px-4 pb-2 text-xs text-gray-400">
        sourced from: {event.source.replace('_', ' ')}
      </div>
    </Link>
  )
}
