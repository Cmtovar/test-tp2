export interface User {
  id: string
  email: string
  display_name: string | null
  created_at: string
}

export interface AuthResponse {
  user: User
  token: string
}
