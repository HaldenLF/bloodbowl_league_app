import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { logIn, postJson, type User } from './api.ts'
import { randomCoachName } from './coachNames.ts'
import { useAction } from './useAction.ts'

const COACH_NAME_PATTERN = String.raw`[A-Za-z0-9]+([ '\-][A-Za-z0-9]+)*`

type Props = {
  onLoggedIn: (user: User) => void
}

export default function SignupForm({ onLoggedIn }: Props) {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState(randomCoachName)
  const [password, setPassword] = useState('')
  const [repeat, setRepeat] = useState('')
  const [accountType, setAccountType] = useState<'coach' | 'commissioner'>('coach')

  const { run, busy, error } = useAction(async () => {
    if (password !== repeat) throw new Error('The two passwords do not match')
    await postJson('/auth/register', {
      email,
      display_name: displayName.trim(),
      password,
      account_type: accountType,
    })
    const user = await logIn(email, password)
    navigate('/')
    onLoggedIn(user)
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void run()
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Create an account</h1>
      <label>
        Email
        <input type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
      </label>
      <label>
        Coach name
        <input
          required
          minLength={3}
          maxLength={32}
          pattern={COACH_NAME_PATTERN}
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
        />
      </label>
      <button type="button" onClick={() => setDisplayName(randomCoachName())}>
        Another name
      </button>
      <p>
        <small>
          3 to 32 letters or digits. Words may be joined by one space, hyphen or apostrophe. Other coaches see this
          name, so it must be unique.
        </small>
      </p>
      <label>
        Password
        <input
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          maxLength={128}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      <label>
        Repeat password
        <input
          type="password"
          autoComplete="new-password"
          required
          value={repeat}
          onChange={(e) => setRepeat(e.target.value)}
        />
      </label>
      <label>
        Account type
        <select value={accountType} onChange={(e) => setAccountType(e.target.value as 'coach' | 'commissioner')}>
          <option value="coach">Coach (join leagues and run teams)</option>
          <option value="commissioner">Commissioner (also create and run leagues)</option>
        </select>
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={busy}>
        {busy ? 'Creating account…' : 'Create account'}
      </button>
      <p>
        Already have an account? <Link to="/">Log in</Link>
      </p>
    </form>
  )
}
