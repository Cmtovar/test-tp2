import { useEffect } from 'react'

interface ToastProps {
  message: string | null
  onClose: () => void
  duration?: number
}

export default function Toast({ message, onClose, duration = 2500 }: ToastProps) {
  useEffect(() => {
    if (!message) return
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [message, onClose, duration])

  if (!message) return null

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-100 bg-gray-900 text-white px-5 py-3 rounded-lg shadow-lg text-sm font-medium">
      {message}
    </div>
  )
}
