import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import EventDetail from '../../pages/EventDetail'
import { fetchEventById } from '../../api/events'
import { mockEvents } from '../../data/mockEvents'

vi.mock('../../api/events', () => ({
  fetchEventById: vi.fn(),
}))

function renderEventDetail(path = `/events/${mockEvents[0].id}`) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/events/:id" element={<EventDetail />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('EventDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state while event request is pending', () => {
    vi.mocked(fetchEventById).mockReturnValue(new Promise(() => {}))

    renderEventDetail()

    expect(screen.getByText('Loading...')).toBeTruthy()
  })

  it('shows not found state when API returns null', async () => {
    vi.mocked(fetchEventById).mockResolvedValue(null)

    renderEventDetail('/events/does-not-exist')

    expect(await screen.findByText('Event not found')).toBeTruthy()
    expect(screen.getByRole('link', { name: 'Back to home' })).toBeTruthy()
  })

  it('renders event details when event is returned', async () => {
    vi.mocked(fetchEventById).mockResolvedValue({
      ...mockEvents[0],
      source: 'seed_data',
      source_url: 'https://example.com/original-post',
      venue_name: 'The Metro',
      venue_address: '3730 N Clark St',
      price_min: 25,
      price_max: 45,
      is_free: false,
    })

    renderEventDetail()

    expect(await screen.findByRole('heading', { name: mockEvents[0].title })).toBeTruthy()
    expect(screen.getByText('seed data')).toBeTruthy()
    expect(screen.getByRole('link', { name: 'link to original posting' })).toBeTruthy()
    expect(screen.getByText('$25–$45')).toBeTruthy()
    expect(screen.getByText('The Metro')).toBeTruthy()
  })

  it('shows free label for free events', async () => {
    vi.mocked(fetchEventById).mockResolvedValue({
      ...mockEvents[2],
      is_free: true,
      price_min: 0,
      price_max: 0,
    })

    renderEventDetail(`/events/${mockEvents[2].id}`)

    expect(await screen.findByText('Free')).toBeTruthy()
  })
})
