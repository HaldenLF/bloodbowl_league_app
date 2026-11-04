import { useState, type FormEvent } from 'react'
import { postJson, type Season } from './api.ts'
import { useAction } from './useAction.ts'

type Props = {
  leagueId: number
  onCreated: () => void
}

export default function CreateSeasonForm({ leagueId, onCreated }: Props) {
  const [name, setName] = useState('')
  const [format, setFormat] = useState<Season['format']>('11s')
  const [startingTreasury, setStartingTreasury] = useState(1_000_000)

  const { run, busy, error } = useAction(async () => {
    await postJson(`/leagues/${leagueId}/seasons`, { name, format, starting_treasury: startingTreasury })
    setName('')
    onCreated()
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void run()
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>New season</h3>
      <label>
        Name
        <input required maxLength={100} value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      <label>
        Format
        <select value={format} onChange={(e) => setFormat(e.target.value as Season['format'])}>
          <option value="11s">11s</option>
          <option value="7s">7s</option>
          <option value="dungeon_bowl">Dungeon Bowl</option>
        </select>
      </label>
      <label>
        Starting treasury (gold)
        <input
          type="number"
          min={0}
          step={10_000}
          required
          value={startingTreasury}
          onChange={(e) => setStartingTreasury(e.target.valueAsNumber)}
        />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={busy}>
        {busy ? 'Creating…' : 'Create season'}
      </button>
    </form>
  )
}
