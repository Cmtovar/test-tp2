import type { Event } from '../types/event'

const API_BASE = '/api/saves'

export interface SavedEventEntry {
  event_id: string
  saved_at: string
  event: Event
}

export interface SavedEventsListResponse {
  data: SavedEventEntry[]
  count: number
}

async function readError(res: Response): Promise<string> {
  try {
    const body = await res.json()
    if (typeof body?.detail === 'string') return body.detail
  } catch {
    /* ignore */
  }
  return `Request failed (HTTP ${res.status})`
}

function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` }
}

export async function getSavedEvents(token: string): Promise<SavedEventsListResponse> {
  const res = await fetch(API_BASE, { headers: authHeaders(token) })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function saveEvent(token: string, eventId: string): Promise<void> {
  const res = await fetch(API_BASE, {
    method: 'POST',
    headers: { ...authHeaders(token), 'Content-Type': 'application/json' },
    body: JSON.stringify({ event_id: eventId }),
  })
  if (!res.ok && res.status !== 409) throw new Error(await readError(res))
}

export async function unsaveEvent(token: string, eventId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/${eventId}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  })
  if (!res.ok && res.status !== 404) throw new Error(await readError(res))
}

export async function checkSaved(token: string, eventId: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/check/${eventId}`, { headers: authHeaders(token) })
  if (!res.ok) throw new Error(await readError(res))
  const body: { is_saved: boolean } = await res.json()
  return body.is_saved
}
