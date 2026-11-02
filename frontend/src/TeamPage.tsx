import { Link, useParams } from 'react-router'
import { type Player, type Race, type Team, type TeamValue } from './api.ts'
import { gold, target } from './format.ts'
import { useApi } from './useApi.ts'

export default function TeamPage() {
  const { teamId } = useParams()
  const team = useApi<Team>(`/teams/${teamId}`)
  const players = useApi<Player[]>(`/teams/${teamId}/players`)
  const value = useApi<TeamValue>(`/teams/${teamId}/value`)

  if (team.error) {
    return (
      <section>
        <p role="alert">{team.error}</p>
        <Link to="/">Back to my leagues</Link>
      </section>
    )
  }
  if (!team.data) {
    return <p>Loading…</p>
  }
  const t = team.data

  return (
    <section>
      <Link to={`/seasons/${t.season_id}`}>← Season</Link>
      <h2>{t.name}</h2>
      <p>
        <RaceName raceId={t.race_id} /> · Coach: {t.coach.display_name} · Treasury: {gold(t.treasury)}
      </p>

      <h3>Roster</h3>
      {players.error && <p role="alert">{players.error}</p>}
      {players.data?.length === 0 && <p>No players yet.</p>}
      {players.data && players.data.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Position</th>
              <th>MA</th>
              <th>ST</th>
              <th>AG</th>
              <th>PA</th>
              <th>AV</th>
              <th>TD</th>
              <th>Cas</th>
              <th>MVP</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {players.data.map((player) => (
              <tr key={player.id}>
                <td>{player.number}</td>
                <td>{player.name ?? '—'}</td>
                <td>{player.position.name}</td>
                <td>{player.position.movement}</td>
                <td>{player.position.strength}</td>
                <td>{target(player.position.agility)}</td>
                <td>{target(player.position.passing)}</td>
                <td>{target(player.position.armor)}</td>
                <td>{player.touchdowns}</td>
                <td>{player.casualties}</td>
                <td>{player.mvps}</td>
                <td>{player.missing_next_game ? 'Misses next game' : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h3>Staff and extras</h3>
      <ul>
        <li>Re-rolls: {t.re_rolls}</li>
        <li>Assistant coaches: {t.assistant_coaches}</li>
        <li>Cheerleaders: {t.cheerleaders}</li>
        <li>Apothecary: {t.apothecary ? 'Yes' : 'No'}</li>
        <li>Dedicated fans: {t.dedicated_fans}</li>
      </ul>

      <h3>Team value</h3>
      {value.error && <p role="alert">{value.error}</p>}
      {value.data && (
        <ul>
          <li>Players: {gold(value.data.players)}</li>
          <li>Re-rolls: {gold(value.data.re_rolls)}</li>
          <li>Staff: {gold(value.data.staff)}</li>
          <li>
            <strong>Total: {gold(value.data.total)}</strong>
          </li>
        </ul>
      )}
    </section>
  )
}

function RaceName({ raceId }: { raceId: number }) {
  const race = useApi<Race>(`/races/${raceId}`)
  return <>{race.data?.name ?? '…'}</>
}
