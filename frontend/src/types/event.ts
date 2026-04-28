export interface Event {
  id: string
  title: string
  description: string | null
  category: string | null
  subcategory: string | null
  start_datetime: string
  end_datetime: string | null
  venue_name: string | null
  venue_address: string | null
  neighborhood: string | null
  lat: number | null
  lng: number | null
  price_min: number | null
  price_max: number | null
  is_free: boolean | null
  ticket_url: string | null
  source_url: string | null
  source: string
  image_url: string | null
  status: string | null
  tags: string[] | null
  popularity: number | null
}

export interface EventListResponse {
  data: Event[]
  count: number
}

export interface EventCardProps {
  event: Event
  isSaved?: boolean
  onSaveToggle?: (id: string) => void
}
