import { Link } from 'react-router'
import { type MyTeam } from './api.ts'
import { gold } from './format.ts'
import { useApi } from './useApi.ts'

export default function MyTeams() {
  const teams = useApi<MyTeam[]>('/me/teams')

  if (teams.error) {
    return <p role="alert">{teams.error}</p>
  }
  if (!teams.data) {
    return <p>Loading…</p>
  }
  const current = teams.data.filter((team) => team.season.is_active)
  const past = teams.data.filter((team) => !team.season.is_active)

  return (
    <section>
      <h2>My teams</h2>
      {teams.data.length === 0 && (
        <p>
          You have no teams yet. Join a league under <Link to="/leagues">Leagues</Link>, then create a team in one of
          its seasons.
        </p>
      )}
      {current.length > 0 && <TeamList title="Current seasons" teams={current} />}
      {past.length > 0 && <TeamList title="Past seasons" teams={past} />}
    </section>
  )
}

function TeamList({ title, teams }: { title: string; teams: MyTeam[] }) {
  return (
    <>
      <h3>{title}</h3>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Team</th>
              <th>Race</th>
              <th>League</th>
              <th>Season</th>
              <th>TV</th>
              <th>Treasury</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr key={team.id}>
                <td>
                  <Link to={`/teams/${team.id}`}>{team.name}</Link>
                </td>
                <td>{team.race.name}</td>
                <td>
                  <Link to={`/leagues/${team.season.league.id}`}>{team.season.league.name}</Link>
                </td>
                <td>
                  <Link to={`/seasons/${team.season.id}`}>{team.season.name}</Link> ({team.season.format})
                </td>
                <td>{gold(team.team_value)}</td>
                <td>{gold(team.treasury)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
