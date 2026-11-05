import { useState } from 'react'
import { Link, useParams } from 'react-router'
import { postJson, type League, type Player, type Race, type RosterPlayer, type Season, type Team, type TeamValue, type User } from './api.ts'
import { gold } from './format.ts'
import EditPlayerForm from './EditPlayerForm.tsx'
import HirePlayerForm from './HirePlayerForm.tsx'
import RosterTable from './RosterTable.tsx'
import { useApi } from './useApi.ts'
import TeamExtras from './TeamExtras.tsx'


type Props = {
  user: User
}

export default function TeamPage({ user }: Props) {
  const { teamId } = useParams()
  const [reloads, setReloads] = useState(0)
  const [actionError, setActionError] = useState<string | null>(null)
  const [editing, setEditing] = useState<Player | null>(null)
  const team = useApi<Team>(`/teams/${teamId}`, reloads)
  const players = useApi<RosterPlayer[]>(`/teams/${teamId}/players`, reloads)
  const value = useApi<TeamValue>(`/teams/${teamId}/value`, reloads)
  const season = useApi<Season>(team.data ? `/seasons/${team.data.season_id}` : null)
  const league = useApi<League>(season.data ? `/leagues/${season.data.league_id}` : null)

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
  const canEdit = t.coach.id === user.id || league.data?.owner.id === user.id

  function reload() {
    setReloads((count) => count + 1)
  }

  async function fire(player: Player) {
    const label = player.name ? `#${player.number} ${player.name}` : `#${player.number}`
    if (!window.confirm(`Fire ${label}? They leave the roster for good, and there is no refund.`)) return
    setActionError(null)
    try {
      await postJson(`/players/${player.id}/fire`, {})
      reload()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Something went wrong')
    }
  }

  return (
    <section>
      <Link to={`/seasons/${t.season_id}`} className="no-print">
        ← Season
      </Link>
      <h2>{t.name}</h2>
      <button type="button" onClick={() => window.print()}>
        Print roster
      </button>

      <h3>Roster</h3>
      {players.error && <p role="alert">{players.error}</p>}
      {actionError && <p role="alert">{actionError}</p>}
      {players.data?.length === 0 && <p>No players yet.</p>}
      {players.data && players.data.length > 0 && (
        <RosterTable
          players={players.data}
          canEdit={canEdit}
          onEdit={setEditing}
          onFire={(player) => void fire(player)}
        />
      )}
      {canEdit && editing && (
        <EditPlayerForm
          key={editing.id}
          player={editing}
          onSaved={() => {
            setEditing(null)
            reload()
          }}
          onCancel={() => setEditing(null)}
        />
      )}
      {canEdit && (
        <HirePlayerForm
          teamId={t.id}
          raceId={t.race_id}
          availablePlayers={players.data?.filter((player) => !player.missing_next_game).length ?? 0}
          onHired={reload}
        />
      )}
        <h3>Team info</h3>
        <table>
          <tbody>
            <tr>
              <th scope="row">Team Name</th>
              <td>{t.name}</td>
            </tr>
            <tr>
              <th scope="row">Coach</th>
              <td>{t.coach.display_name}</td>
            </tr>
            <tr>
              <th scope="row">Team Race</th>
              <td>
                <RaceName raceId={t.race_id} />
              </td>
            </tr>
            <tr>
              <th scope="row">Treasury</th>
              <td>{gold(t.treasury)}</td>
            </tr>
            <tr>
              <th scope="row">TV</th>
              <td>{value.data ? gold(value.data.total) : (value.error ?? '…')}</td>
            </tr>
          </tbody>
        </table>
        <TeamExtras teamId={t.id} treasury={t.treasury} canEdit={canEdit} reloadKey={reloads} onBought={reload} />
    </section>
  )
}

function RaceName({ raceId }: { raceId: number }) {
  const race = useApi<Race>(`/races/${raceId}`)
  return <>{race.data?.name ?? '…'}</>
}
