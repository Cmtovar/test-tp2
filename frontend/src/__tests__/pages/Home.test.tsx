import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Home from '../../pages/Home'
import { mockEvents } from '../../data/mockEvents'
import { fetchEvents } from '../../api/events'

vi.mock('../../api/events', () => ({
  fetchEvents: vi.fn(),
}))

describe('Home', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders events returned by fetchEvents', async () => {
    vi.mocked(fetchEvents).mockResolvedValue([mockEvents[0]])

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    )

    expect(await screen.findByText(mockEvents[0].title)).toBeTruthy()
    expect(screen.getByText('Explore')).toBeTruthy()
  })

  it('shows empty state when no events are returned', async () => {
    vi.mocked(fetchEvents).mockResolvedValue([])

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    )

    expect(await screen.findByText('No events found')).toBeTruthy()
  })

  it('shows loading state while events request is pending', () => {
    vi.mocked(fetchEvents).mockReturnValue(new Promise(() => {}))

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    )

    expect(screen.getByText('Loading events...')).toBeTruthy()
  })

  it('renders disabled location input', () => {
    vi.mocked(fetchEvents).mockResolvedValue([mockEvents[0]])

    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    )

    const input = screen.getByPlaceholderText('city / zip code')
    expect(input).toBeTruthy()
    expect(input.getAttribute('disabled')).not.toBeNull()
  })
})
