import { useState } from 'react'
import { logOut, type User } from './api.ts'
import LoginForm from './LoginForm.tsx'
import MyLeagues from './MyLeagues.tsx'

export default function App() {
  const [user, setUser] = useState<User | null>(null)

  if (user === null) {
    return <LoginForm onLoggedIn={setUser} />
  }

  function handleLogOut() {
    logOut()
    setUser(null)
  }

  return (
    <main>
      <p>
        Logged in as <strong>{user.display_name}</strong> ({user.account_type})
      </p>
      <button type="button" onClick={handleLogOut}>
        Log out
      </button>
      <MyLeagues user={user} />
    </main>
  )
}
