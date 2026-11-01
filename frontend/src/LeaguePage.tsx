import { Link, useParams } from 'react-router'
import { type League, type Member, type Season } from './api.ts'
import { useApi } from './useApi.ts'

export default function LeaguePage() {
  const { leagueId } = useParams()
  const league = useApi<League>(`/leagues/${leagueId}`)
  const seasons = useApi<Season[]>(`/leagues/${leagueId}/seasons`)
  const members = useApi<Member[]>(`/leagues/${leagueId}/members`)

  if (league.error) {
    return (
      <section>
        <p role="alert">{league.error}</p>
        <Link to="/">Back to my leagues</Link>
      </section>
    )
  }
  if (!league.data) {
    return <p>Loading…</p>
  }

  return (
    <section>
      <Link to="/">← My leagues</Link>
      <h2>{league.data.name}</h2>
      <p>Run by {league.data.owner.display_name}</p>

      <h3>Seasons</h3>
      {seasons.error && <p role="alert">{seasons.error}</p>}
      {seasons.data?.length === 0 && <p>No seasons yet.</p>}
      <ul>
        {seasons.data?.map((season) => (
          <li key={season.id}>
            {season.name} ({season.format}){season.is_active ? '' : ' — finished'}
          </li>
        ))}
      </ul>

      <h3>Members</h3>
      {members.error && <p role="alert">{members.error}</p>}
      <ul>
        {members.data?.map((member) => (
          <li key={member.user.id}>{member.user.display_name}</li>
        ))}
      </ul>
    </section>
  )
}
