import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import EventCard from '../../components/EventCard'
import { mockEvents } from '../../data/mockEvents'

describe('EventCard', () => {
  it('renders event content and source attribution', () => {
    render(
      <MemoryRouter>
        <EventCard event={mockEvents[0]} />
      </MemoryRouter>,
    )

    expect(screen.getByText(mockEvents[0].title)).toBeTruthy()
    expect(screen.getByText(`sourced from: ${mockEvents[0].source}`)).toBeTruthy()
  })

  it('calls onSaveToggle with event id when save button is clicked', () => {
    const onSaveToggle = vi.fn()

    render(
      <MemoryRouter>
        <EventCard event={mockEvents[0]} onSaveToggle={onSaveToggle} />
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Save event' }))
    expect(onSaveToggle).toHaveBeenCalledWith(mockEvents[0].id)
  })

  it('links to the event detail page', () => {
    render(
      <MemoryRouter>
        <EventCard event={mockEvents[0]} />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link').getAttribute('href')).toBe(`/events/${mockEvents[0].id}`)
  })

  it('shows unsave aria label when isSaved is true', () => {
    render(
      <MemoryRouter>
        <EventCard event={mockEvents[0]} isSaved />
      </MemoryRouter>,
    )

    expect(screen.getByRole('button', { name: 'Unsave event' })).toBeTruthy()
  })

  it('renders Free price label for free events', () => {
    render(
      <MemoryRouter>
        <EventCard event={mockEvents[2]} />
      </MemoryRouter>,
    )

    expect(screen.getByText('Free')).toBeTruthy()
  })

  it('renders placeholder when image_url is missing', () => {
    render(
      <MemoryRouter>
        <EventCard event={mockEvents[0]} />
      </MemoryRouter>,
    )

    expect(screen.queryByRole('img', { name: mockEvents[0].title })).toBeNull()
  })
})
