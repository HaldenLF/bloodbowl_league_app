import { useState, type FormEvent } from 'react'
import { postJson, type RaceDetail } from './api.ts'
import { gold } from './format.ts'
import { useAction } from './useAction.ts'
import { useApi } from './useApi.ts'

const MIN_PLAYERS_FOR_A_GAME = 11

type Props = {
  teamId: number
  raceId: number
  availablePlayers: number
  onHired: () => void
}

export default function HirePlayerForm({ teamId, raceId, availablePlayers, onHired }: Props) {
  const race = useApi<RaceDetail>(`/races/${raceId}`)
  const [positionId, setPositionId] = useState('')
  const [name, setName] = useState('')

  const journeymenAllowed = availablePlayers < MIN_PLAYERS_FOR_A_GAME
  const positions = race.data?.positions.filter(
    (position) => journeymenAllowed || !position.name.toLowerCase().startsWith('journeyman'),
  )

  const { run, busy, error } = useAction(async () => {
    await postJson(`/teams/${teamId}/players`, {
      position_id: Number(positionId),
      name: name.trim() || null,
    })
    setName('')
    onHired()
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void run()
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Hire a player</h3>
      <label>
        Position
        <select required value={positionId} onChange={(e) => setPositionId(e.target.value)}>
          <option value="" disabled>
            {positions ? 'Choose a position' : 'Loading positions…'}
          </option>
          {positions?.map((position) => (
            <option key={position.id} value={position.id}>
              {position.name} — {gold(position.cost)} (max {position.max_allowed})
            </option>
          ))}
        </select>
      </label>
      <label>
        Name (optional)
        <input maxLength={100} value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      {(error ?? race.error) && <p role="alert">{error ?? race.error}</p>}
      <button type="submit" disabled={busy || !positions}>
        {busy ? 'Hiring…' : 'Hire'}
      </button>
    </form>
  )
}
