import { useEffect, useState } from 'react'
import { api, type League, type User } from './api.ts'
import JoinLeagueForm from './JoinLeagueForm.tsx'

type Props = {
  user: User
}

export default function MyLeagues({ user }: Props) {
  const [leagues, setLeagues] = useState<League[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [reloads, setReloads] = useState(0)

  useEffect(() => {
    let cancelled = false
    api<League[]>('/leagues')
      .then((data) => {
        if (!cancelled) setLeagues(data)
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Could not load your leagues')
      })
    return () => {
      cancelled = true
    }
  }, [reloads])

  return (
    <section>
      <h2>My leagues</h2>
      {error && <p role="alert">{error}</p>}
      {leagues === null && !error && <p>Loading…</p>}
      {leagues?.length === 0 && <p>You are not in any leagues yet.</p>}
      {leagues && leagues.length > 0 && (
        <ul>
          {leagues.map((league) => (
            <li key={league.id}>
              <strong>{league.name}</strong> — run by {league.owner.display_name}
              {league.owner.id === user.id && ' (you)'}
            </li>
          ))}
        </ul>
      )}
      <JoinLeagueForm onJoined={() => setReloads((count) => count + 1)} />
    </section>
  )
}
