import { Link, useParams } from 'react-router'
import { type Season, type Team, type User } from './api.ts'
import { gold } from './format.ts'
import { useApi } from './useApi.ts'
import { useState } from  'react'
import CreateTeamForm from './CreateTeamForm.tsx'


type Props = {
  user: User
}


export default function SeasonPage({ user }: Props) {
  const { seasonId } = useParams()
  const season = useApi<Season>(`/seasons/${seasonId}`)
  const [reloads, setReloads] = useState(0)
  const teams = useApi<Team[]>(`/seasons/${seasonId}/teams`, reloads)


  if (season.error) {
    return (
      <section>
        <p role="alert">{season.error}</p>
        <Link to="/leagues">Back to my leagues</Link>
      </section>
    )
  }
  if (!season.data) {
    return <p>Loading…</p>
  }

  const hasTeam = teams.data?.some((team) => team.coach.id === user.id) ?? true


  return (
    <section>
      <Link to={`/leagues/${season.data.league_id}`}>← League</Link>
      <h2>{season.data.name}</h2>
      <p>
        Format: {season.data.format} · Starting treasury: {gold(season.data.starting_treasury)}
      </p>

      <h3>Teams</h3>
      {teams.error && <p role="alert">{teams.error}</p>}
      {teams.data?.length === 0 && <p>No teams yet.</p>}
      <ul>
        {teams.data?.map((team) => (
          <li key={team.id}>
            <Link to={`/teams/${team.id}`}>{team.name}</Link> — coached by {team.coach.display_name}
          </li>
        ))}
      </ul>
      {!hasTeam && <CreateTeamForm seasonId={season.data.id} onCreated={() => setReloads((count) => count + 1)} />}
    </section>
  )
}
