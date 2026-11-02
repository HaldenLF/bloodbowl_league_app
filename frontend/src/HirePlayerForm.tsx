import { useState, type FormEvent } from 'react'
import { postJson, type RaceDetail } from './api.ts'
import { gold } from './format.ts'
import { useAction } from './useAction.ts'
import { useApi } from './useApi.ts'

type Props = {
  teamId: number
  raceId: number
  onHired: () => void
}

export default function HirePlayerForm({ teamId, raceId, onHired }: Props) {
  const race = useApi<RaceDetail>(`/races/${raceId}`)
  const [positionId, setPositionId] = useState('')
  const [number, setNumber] = useState('')
  const [name, setName] = useState('')

  const { run, busy, error } = useAction(async () => {
    await postJson(`/teams/${teamId}/players`, {
      position_id: Number(positionId),
      number: Number(number),
      name: name.trim() || null,
    })
    setNumber('')
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
            {race.data ? 'Choose a position' : 'Loading positions…'}
          </option>
          {race.data?.positions.map((position) => (
            <option key={position.id} value={position.id}>
              {position.name} — {gold(position.cost)} (max {position.max_allowed})
            </option>
          ))}
        </select>
      </label>
      <label>
        Number
        <input type="number" min={1} max={99} required value={number} onChange={(e) => setNumber(e.target.value)} />
      </label>
      <label>
        Name (optional)
        <input maxLength={100} value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      {(error ?? race.error) && <p role="alert">{error ?? race.error}</p>}
      <button type="submit" disabled={busy || !race.data}>
        {busy ? 'Hiring…' : 'Hire'}
      </button>
    </form>
  )
}
