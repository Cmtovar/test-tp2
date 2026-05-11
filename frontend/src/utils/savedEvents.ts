const STORAGE_KEY = 'chipulse_saved_events'

export function getSavedIds(): Set<string> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? new Set(JSON.parse(raw)) : new Set()
  } catch {
    return new Set()
  }
}

export function toggleSave(id: string): void {
  const ids = getSavedIds()
  if (ids.has(id)) {
    ids.delete(id)
  } else {
    ids.add(id)
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]))
}
