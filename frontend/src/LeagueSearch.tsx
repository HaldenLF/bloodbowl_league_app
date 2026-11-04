import { useState, type FormEvent } from 'react'
import { api, postJson, type LeagueSearchResult, type Membership } from './api.ts'

type Props = {
  memberOf: Set<number>
  onJoined: () => void
}

export default function LeagueSearch({ memberOf, onJoined }: Props) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<LeagueSearchResult[] | null>(null)
  const [requested, setRequested] = useState<Set<number>>(new Set())
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  async function act(action: () => Promise<void>) {
    setBusy(true)
    setError(null)
    setMessage(null)
    try {
      await action()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void act(async () => {
      setResults(await api<LeagueSearchResult[]>(`/leagues/search?q=${encodeURIComponent(query.trim())}`))
    })
  }

  function join(league: LeagueSearchResult) {
    void act(async () => {
      const membership = await postJson<Membership>(`/leagues/${league.id}/join`, {})
      setRequested((ids) => new Set(ids).add(league.id))
      if (membership.status === 'active') {
        setMessage(`You joined ${league.name}.`)
        onJoined()
      } else {
        setMessage(`Request sent. ${league.owner.display_name} will approve or reject it.`)
      }
    })
  }

  function joinButton(league: LeagueSearchResult) {
    if (memberOf.has(league.id)) return <small>Member</small>
    if (requested.has(league.id)) return <small>Requested</small>
    return (
      <button type="button" disabled={busy} onClick={() => join(league)}>
        {league.join_policy === 'open' ? 'Join' : 'Ask to join'}
      </button>
    )
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Find a league</h3>
      <label>
        League name
        <input
          type="search"
          required
          minLength={2}
          maxLength={100}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </label>
      <button type="submit" disabled={busy}>
        Search
      </button>
      {error && <p role="alert">{error}</p>}
      {message && <p>{message}</p>}
      {results?.length === 0 && <p>No leagues found. Invite-only leagues need a join code.</p>}
      {results && results.length > 0 && (
        <ul>
          {results.map((league) => (
            <li key={league.id}>
              {league.name} — run by {league.owner.display_name}{' '}
              {league.join_policy === 'approval' ? '(needs approval)' : '(open)'} {joinButton(league)}
            </li>
          ))}
        </ul>
      )}
    </form>
  )
}
