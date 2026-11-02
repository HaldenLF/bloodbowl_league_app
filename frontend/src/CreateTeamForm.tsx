import { useState, type FormEvent } from 'react'
import { postJson, type Race } from './api.ts'
import { useAction } from './useAction.ts'
import { useApi } from './useApi.ts'

type Props = {
  seasonId: number
  onCreated: () => void
}

export default function CreateTeamForm({ seasonId, onCreated }: Props) {
  const races = useApi<Race[]>('/races')
  const [name, setName] = useState('')
  const [raceId, setRaceId] = useState('')

  const { run, busy, error } = useAction(async () => {
    await postJson(`/seasons/${seasonId}/teams`, { name, race_id: Number(raceId) })
    setName('')
    onCreated()
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void run()
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Create your team</h3>
      <label>
        Team name
        <input required maxLength={150} value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      <label>
        Race
        <select required value={raceId} onChange={(e) => setRaceId(e.target.value)}>
          <option value="" disabled>
            {races.data ? 'Choose a race' : 'Loading races…'}
          </option>
          {races.data?.map((race) => (
            <option key={race.id} value={race.id}>
              {race.name}
            </option>
          ))}
        </select>
      </label>
      {(error ?? races.error) && <p role="alert">{error ?? races.error}</p>}
      <button type="submit" disabled={busy || !races.data}>
        {busy ? 'Creating…' : 'Create team'}
      </button>
    </form>
  )
}
