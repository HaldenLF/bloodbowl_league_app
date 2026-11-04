import { useState } from 'react'
import { api, postJson, type JoinCode, type Member } from './api.ts'
import { useApi } from './useApi.ts'

type Props = {
  leagueId: number
  onMembersChanged: () => void
}

export default function CommissionerPanel({ leagueId, onMembersChanged }: Props) {
  const [reloads, setReloads] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const code = useApi<JoinCode>(`/leagues/${leagueId}/join-code`, reloads)
  const requests = useApi<Member[]>(`/leagues/${leagueId}/join-requests`, reloads)
  const joinCode = code.data?.join_code

  async function act(action: () => Promise<unknown>) {
    setBusy(true)
    setError(null)
    try {
      await action()
      setReloads((count) => count + 1)
      onMembersChanged()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  async function copyCode(value: string) {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
    } catch {
      setError('Could not copy; select the code and copy it by hand')
    }
  }

  function regenerate() {
    if (!window.confirm('Make a new join code? The current code stops working straight away.')) return
    setCopied(false)
    void act(() => postJson(`/leagues/${leagueId}/join-code/regenerate`, {}))
  }

  function approve(member: Member) {
    void act(() => postJson(`/leagues/${leagueId}/join-requests/${member.user.id}/approve`, {}))
  }

  function reject(member: Member) {
    if (!window.confirm(`Reject ${member.user.display_name}'s request to join?`)) return
    void act(() => api(`/leagues/${leagueId}/join-requests/${member.user.id}`, { method: 'DELETE' }))
  }

  return (
    <>
      <h3>Commissioner</h3>
      {(error ?? code.error ?? requests.error) && <p role="alert">{error ?? code.error ?? requests.error}</p>}

      <p>
        Join code: {joinCode ? <code>{joinCode}</code> : '…'}{' '}
        {joinCode && (
          <button type="button" onClick={() => void copyCode(joinCode)}>
            {copied ? 'Copied' : 'Copy'}
          </button>
        )}{' '}
        <button type="button" onClick={regenerate} disabled={busy}>
          New code
        </button>
      </p>
      <p>
        <small>Anyone with this code joins without needing approval. Share it privately.</small>
      </p>

      <h4>Join requests</h4>
      {requests.data?.length === 0 && <p>No pending requests.</p>}
      <ul>
        {requests.data?.map((member) => (
          <li key={member.user.id}>
            {member.user.display_name}{' '}
            <button type="button" onClick={() => approve(member)} disabled={busy}>
              Approve
            </button>{' '}
            <button type="button" onClick={() => reject(member)} disabled={busy}>
              Reject
            </button>
          </li>
        ))}
      </ul>
    </>
  )
}
