export type User = {
  id: number
  email: string
  display_name: string
  account_type: 'coach' | 'commissioner' | 'super_admin'
}


export type UserPublic = {
  id: number
  display_name: string
}


export type League = {
  id: number
  name: string
  join_policy: 'invite_only' | 'open' | 'approval'
  owner: UserPublic
  created_at: string
}


export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

let accessToken: string | null = null

export function setAccessToken(token: string | null): void {
  accessToken = token
}

function errorMessage(status: number, body: unknown): string {
  if (body && typeof body === 'object') {
    const { detail, error } = body as { detail?: unknown; error?: unknown }
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return 'Please check the form and try again'
    if (typeof error === 'string') return error
  }
  return `Request failed (${status})`
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

  const response = await fetch(`/api${path}`, { ...options, headers })
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null)
    throw new ApiError(response.status, errorMessage(response.status, body))
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export async function logIn(email: string, password: string): Promise<User> {
  const form = new URLSearchParams({ username: email, password })
  const { access_token } = await api<{ access_token: string }>('/auth/login', { method: 'POST', body: form })
  setAccessToken(access_token)
  return api<User>('/auth/me')
}

export function logOut(): void {
  setAccessToken(null)
}
