import { useState } from 'react'
import { Link } from 'react-router'
import { type League, type User } from './api.ts'
import JoinLeagueForm from './JoinLeagueForm.tsx'
import { useApi } from './useApi.ts'

type Props = {
  user: User
}

export default function MyLeagues({ user }: Props) {
  const [reloads, setReloads] = useState(0)
  const { data: leagues, error, loading } = useApi<League[]>('/leagues', reloads)


  return (
    <section>
      <h2>My leagues</h2>
      {error && <p role="alert">{error}</p>}
      {loading && !leagues && <p>Loading…</p>}
      {leagues?.length === 0 && <p>You are not in any leagues yet.</p>}
      {leagues && leagues.length > 0 && (
        <ul>
          {leagues.map((league) => (
            <li key={league.id}>
              <Link to={`/leagues/${league.id}`}>{league.name}</Link> — run by {league.owner.display_name}
              {league.owner.id === user.id && ' (you)'}
            </li>
          ))}
        </ul>
      )}
      <JoinLeagueForm onJoined={() => setReloads((count) => count + 1)} />
    </section>
  )
}
