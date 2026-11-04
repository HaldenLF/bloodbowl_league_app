import { useState } from 'react'
import { Link, Route, Routes } from 'react-router'
import { logOut, type User } from './api.ts'
import LeaguePage from './LeaguePage.tsx'
import LoginForm from './LoginForm.tsx'
import MyLeagues from './MyLeagues.tsx'
import SeasonPage from './SeasonPage.tsx'
import SignupForm from './SignupForm.tsx'
import TeamPage from './TeamPage.tsx'

export default function App() {
  const [user, setUser] = useState<User | null>(null)

  if (user === null) {
    return (
      <Routes>
        <Route path="/signup" element={<SignupForm onLoggedIn={setUser} />} />
        <Route path="*" element={<LoginForm onLoggedIn={setUser} />} />
      </Routes>
    )
  }

  function handleLogOut() {
    logOut()
    setUser(null)
  }

  return (
    <main>
      <header>
        Logged in as <strong>{user.display_name}</strong> ({user.account_type}){' '}
        <button type="button" onClick={handleLogOut}>
          Log out
        </button>
      </header>
      <Routes>
        <Route path="/" element={<MyLeagues user={user} />} />
        <Route path="/leagues/:leagueId" element={<LeaguePage user={user} />} />
        <Route path="/seasons/:seasonId" element={<SeasonPage user={user} />} />
        <Route path="/teams/:teamId" element={<TeamPage user={user} />} />
        <Route path="*" element={<NotFound />} />

      </Routes>
    </main>
  )
}


function NotFound() {
  return (
    <section>
      <p>Page not found.</p>
      <Link to="/">Back to my leagues</Link>
    </section>
  )
}