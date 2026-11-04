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


export type Season = {
  id: number
  league_id: number
  name: string
  format: '16s' | '7s' | 'dungeon_bowl'
  is_active: boolean
  starting_treasury: number
}


export type Member = {
  user: UserPublic
  status: 'pending' | 'active'
  joined_at: string
}


export type Team = {
  id: number
  season_id: number
  race_id: number
  name: string
  coach: UserPublic
  treasury: number
  re_rolls: number
  assistant_coaches: number
  cheerleaders: number
  apothecary: number
  dedicated_fans: number
  created_at: string
}

export type Race = {
  id: number
  name: string
}

export type Position = {
  id: number
  name: string
  max_allowed: number
  movement: number
  strength: number
  agility: number
  passing: number
  armor: number
  skill_list: string | null
  cost: number
}


export type RaceDetail = Race & {
  positions: Position[]
}


export type Player = {
  id: number
  team_id: number
  number: number
  name: string | null
  touchdowns: number
  casualties: number
  mvps: number
  niggling_injuries: number
  missing_next_game: boolean
  dead: boolean
  fired: boolean
  position: Position
}


export type ShopItem = {
  item: 're_roll' | 'assistant_coach' | 'cheerleader' | 'apothecary' | 'dedicated_fan'
  owned: number
  maximum: number
  price: number | null
  unavailable_reason: string | null
}


export type TeamValue = {
  players: number
  re_rolls: number
  staff: number
  total: number
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


function sendJson<T>(method: 'POST' | 'PATCH', path: string, body: unknown): Promise<T> {
  return api<T>(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}


export function postJson<T>(path: string, body: unknown): Promise<T> {
  return sendJson<T>('POST', path, body)
}


export function patchJson<T>(path: string, body: unknown): Promise<T> {
  return sendJson<T>('PATCH', path, body)
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
