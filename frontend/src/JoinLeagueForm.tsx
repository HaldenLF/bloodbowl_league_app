import { useState, type FormEvent } from 'react'
import { api } from './api.ts'

type Props = {
  onJoined: () => void
}

export default function JoinLeagueForm({ onJoined }: Props) {
  const [code, setCode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await api('/leagues/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ join_code: code }),
      })
      setCode('')
      onJoined()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Join a league</h3>
      <label>
        Join code
        <input required autoComplete="off" value={code} onChange={(e) => setCode(e.target.value)} />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={busy}>
        {busy ? 'Joining…' : 'Join'}
      </button>
    </form>
  )
}
