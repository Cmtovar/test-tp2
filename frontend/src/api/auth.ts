import type { AuthResponse, User } from '../types/auth'

const API_BASE = '/api/auth'

async function readError(res: Response): Promise<string> {
  try {
    const body = await res.json()
    if (typeof body?.detail === 'string') return body.detail
    if (Array.isArray(body?.detail) && body.detail[0]?.msg) return body.detail[0].msg
  } catch {
    /* ignore */
  }
  return `Request failed (HTTP ${res.status})`
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function registerUser(
  email: string,
  password: string,
  displayName: string,
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, display_name: displayName }),
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}

export async function getCurrentUser(token: string): Promise<User> {
  const res = await fetch(`${API_BASE}/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(await readError(res))
  return res.json()
}
