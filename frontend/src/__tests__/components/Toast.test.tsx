import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import Toast from '../../components/Toast'

describe('Toast', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('does not render when message is null', () => {
    const { container } = render(<Toast message={null} onClose={() => {}} />)

    expect(container.firstChild).toBeNull()
  })

  it('renders message text when provided', () => {
    render(<Toast message="Saved!" onClose={() => {}} />)

    expect(screen.getByText('Saved!')).toBeTruthy()
  })

  it('calls onClose after duration elapses', () => {
    vi.useFakeTimers()
    const onClose = vi.fn()

    render(<Toast message="Soon gone" onClose={onClose} duration={1500} />)
    vi.advanceTimersByTime(1499)
    expect(onClose).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1)
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('clears timer on unmount', () => {
    vi.useFakeTimers()
    const onClose = vi.fn()
    const { unmount } = render(<Toast message="Unmount me" onClose={onClose} duration={1000} />)

    unmount()
    vi.advanceTimersByTime(1000)

    expect(onClose).not.toHaveBeenCalled()
  })
})
