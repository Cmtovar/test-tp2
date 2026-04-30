import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import Navbar from '../../components/Navbar'

describe('Navbar', () => {
  it('renders brand and nav items', () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>,
    )

    expect(screen.getByText('ChiPulse')).toBeTruthy()
    expect(screen.getByRole('link', { name: 'Home' })).toBeTruthy()
    expect(screen.getByRole('link', { name: 'My Events' })).toBeTruthy()
    expect(screen.getByRole('link', { name: 'Profile' })).toBeTruthy()
  })

  it('shows coming soon toast for unimplemented pages', async () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('link', { name: 'My Events' }))
    expect(await screen.findByText('My Events — coming soon')).toBeTruthy()
  })
})
