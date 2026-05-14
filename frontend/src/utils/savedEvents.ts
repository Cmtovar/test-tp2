const STORAGE_KEY = 'chipulse_saved_events'

export function getSavedIds(): Set<string> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? new Set(JSON.parse(raw)) : new Set()
  } catch {
    return new Set()
  }
}

export function persistSavedIds(ids: Set<string>): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]))
}

export function addSavedId(id: string): void {
  const ids = getSavedIds()
  ids.add(id)
  persistSavedIds(ids)
}

export function removeSavedId(id: string): void {
  const ids = getSavedIds()
  ids.delete(id)
  persistSavedIds(ids)
}
