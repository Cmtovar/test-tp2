import { afterEach, describe, expect, it, vi } from 'vitest'

import { fetchEventById, fetchEvents } from '../../api/events'
import { mockEvents } from '../../data/mockEvents'

describe('events api client', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns API events when fetch succeeds', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: [mockEvents[0]], count: 1 }),
    } as Response)
    vi.stubGlobal('fetch', fetchMock)

    const events = await fetchEvents()

    expect(fetchMock).toHaveBeenCalledWith('/api/events')
    expect(events).toHaveLength(1)
    expect(events[0].id).toBe(mockEvents[0].id)
  })

  it('falls back to mock events when list request fails', async () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))

    const events = await fetchEvents()

    expect(warnSpy).toHaveBeenCalled()
    expect(events).toEqual(mockEvents)
  })

  it('falls back to mock events when list request is non-OK', async () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
      } as Response),
    )

    const events = await fetchEvents()

    expect(warnSpy).toHaveBeenCalled()
    expect(events).toEqual(mockEvents)
  })

  it('falls back to local match for fetchEventById when request fails', async () => {
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))

    const event = await fetchEventById('mock-002')

    expect(event?.id).toBe('mock-002')
  })

  it('returns event from API for fetchEventById when request succeeds', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockEvents[1],
    } as Response)
    vi.stubGlobal('fetch', fetchMock)

    const event = await fetchEventById('mock-002')

    expect(fetchMock).toHaveBeenCalledWith('/api/events/mock-002')
    expect(event?.id).toBe('mock-002')
  })

  it('returns null fallback when id is not found in mocks', async () => {
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
      } as Response),
    )

    const event = await fetchEventById('does-not-exist')

    expect(event).toBeNull()
  })
})
