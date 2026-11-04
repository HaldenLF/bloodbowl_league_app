import { useState, type FormEvent } from 'react'
import { patchJson, type Player } from './api.ts'
import { useAction } from './useAction.ts'

type Props = {
  player: Player
  onSaved: () => void
  onCancel: () => void
}

export default function EditPlayerForm({ player, onSaved, onCancel }: Props) {
  const [number, setNumber] = useState(String(player.number))
  const [name, setName] = useState(player.name ?? '')

  const { run, busy, error } = useAction(async () => {
    await patchJson(`/players/${player.id}`, {
      number: Number(number),
      name: name.trim() || null,
    })
    onSaved()
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void run()
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>
        Edit #{player.number} {player.position.name}
      </h3>
      <label>
        Number
        <input
          type="number"
          required
          min={1}
          max={99}
          value={number}
          onChange={(e) => setNumber(e.target.value)}
        />
      </label>
      <label>
        Name (optional)
        <input maxLength={100} value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={busy}>
        {busy ? 'Saving…' : 'Save'}
      </button>{' '}
      <button type="button" onClick={onCancel} disabled={busy}>
        Cancel
      </button>
    </form>
  )
}
