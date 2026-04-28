import type { Event, EventListResponse } from '../types/event'
import { mockEvents } from '../data/mockEvents'

const API_BASE = '/api'

export async function fetchEvents(): Promise<Event[]> {
  try {
    const res = await fetch(`${API_BASE}/events`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data: EventListResponse = await res.json()
    return data.data
  } catch {
    console.warn('API unavailable, using mock data')
    return mockEvents
  }
}

export async function fetchEventById(id: string): Promise<Event | null> {
  try {
    const res = await fetch(`${API_BASE}/events/${id}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch {
    console.warn('API unavailable, using mock data')
    return mockEvents.find((e) => e.id === id) ?? null
  }
}
