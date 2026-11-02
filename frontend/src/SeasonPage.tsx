import { Link, useParams } from 'react-router'
import { type Season, type Team } from './api.ts'
import { gold } from './format.ts'
import { useApi } from './useApi.ts'

export default function SeasonPage() {
  const { seasonId } = useParams()
  const season = useApi<Season>(`/seasons/${seasonId}`)
  const teams = useApi<Team[]>(`/seasons/${seasonId}/teams`)

  if (season.error) {
    return (
      <section>
        <p role="alert">{season.error}</p>
        <Link to="/">Back to my leagues</Link>
      </section>
    )
  }
  if (!season.data) {
    return <p>Loading…</p>
  }

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
    </section>
  )
}
