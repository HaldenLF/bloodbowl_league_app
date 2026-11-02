import { useState } from 'react'
import { Link, Route, Routes } from 'react-router'
import { logOut, type User } from './api.ts'
import LeaguePage from './LeaguePage.tsx'
import LoginForm from './LoginForm.tsx'
import MyLeagues from './MyLeagues.tsx'
import SeasonPage from './SeasonPage.tsx'
import TeamPage from './TeamPage.tsx'

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
      <header>
        Logged in as <strong>{user.display_name}</strong> ({user.account_type}){' '}
        <button type="button" onClick={handleLogOut}>
          Log out
        </button>
      </header>
      <Routes>
        <Route path="/" element={<MyLeagues user={user} />} />
        <Route path="/leagues/:leagueId" element={<LeaguePage />} />
        <Route path="/seasons/:seasonId" element={<SeasonPage />} />
        <Route path="/teams/:teamId" element={<TeamPage />} />
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