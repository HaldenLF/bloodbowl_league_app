import { type Player, type RosterPlayer } from './api.ts'
import { gold, target } from './format.ts'

type Props = {
  players: RosterPlayer[]
  canEdit: boolean
  onEdit: (player: Player) => void
  onFire: (player: Player) => void
}

export default function RosterTable({ players, canEdit, onEdit, onFire }: Props) {
  return (
    <div className="table-scroll">
        <table>
            <thead>
            <tr>
                <th>#</th>
                <th>Name</th>
                <th>Position</th>
                <th>MA</th>
                <th>ST</th>
                <th>AG+</th>
                <th>PA+</th>
                <th>AV+</th>
                <th>Skills and Improvements</th>
                <th>Miss Next Game</th>
                <th>Niggling Injuries</th>
                <th>Comp</th>
                <th>TD</th>
                <th>Int</th>
                <th>Cas</th>
                <th>MVP</th>
                <th>SPP</th>
                <th>Total Value</th>
                {canEdit && <th />}
            </tr>
            </thead>
            <tbody>
            {players.map((player) => (
                <tr key={player.id}>
                <td>{player.number}</td>
                <td>{player.name ?? '—'}</td>
                <td>{player.position.name}</td>
                <td>{player.position.movement}</td>
                <td>{player.position.strength}</td>
                <td>{target(player.position.agility)}</td>
                <td>{target(player.position.passing)}</td>
                <td>{target(player.position.armor)}</td>
                <td>{player.position.skill_list ?? ''}</td>
                <td>{player.missing_next_game ? 'X' : ''}</td>
                <td>{player.niggling_injuries || ''}</td>
                <td>{player.completions}</td>
                <td>{player.touchdowns}</td>
                <td>{player.interceptions}</td>
                <td>{player.casualties}</td>
                <td>{player.mvps}</td>
                <td>{player.spp}</td>
                <td>{gold(player.value)}</td>
                {canEdit && (
                    <td>
                    <button type="button" onClick={() => onEdit(player)}>
                        Edit
                    </button>{' '}
                    <button type="button" onClick={() => onFire(player)}>
                        Fire
                    </button>
                    </td>
                )}
                </tr>
            ))}
            </tbody>
        </table>
    </div>
  )
}
