import { useState } from 'react'
import { Link, Route, Routes, useLocation } from 'react-router'
import { logOut, type User } from './api.ts'
import LeaguePage from './LeaguePage.tsx'
import LoginForm from './LoginForm.tsx'
import MyLeagues from './MyLeagues.tsx'
import SeasonPage from './SeasonPage.tsx'
import SignupForm from './SignupForm.tsx'
import TeamPage from './TeamPage.tsx'
import TopBar from './TopBar.tsx'

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const location = useLocation()

  if (user === null) {
    return (
      <div className="auth-screen">
        <div className="auth-box">
          <Routes>
            <Route path="/signup" element={<SignupForm onLoggedIn={setUser} />} />
            <Route path="*" element={<LoginForm onLoggedIn={setUser} />} />
          </Routes>
        </div>
      </div>
    )
  }

  function handleLogOut() {
    logOut()
    setUser(null)
  }

  return (
    <main>
      <TopBar key={location.pathname} user={user} onLogOut={handleLogOut} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/teams" element={<ComingSoon what="Your teams" />} />
        <Route path="/leagues" element={<MyLeagues user={user} />} />
        <Route path="/leagues/:leagueId" element={<LeaguePage user={user} />} />
        <Route path="/seasons/:seasonId" element={<SeasonPage user={user} />} />
        <Route path="/teams/:teamId" element={<TeamPage user={user} />} />
        <Route path="*" element={<NotFound />} />

      </Routes>
    </main>
  )
}


function Home() {
  return (
    <section>
      <h2>Home</h2>
      <p>Recent results, league tables and your teams will appear here.</p>
    </section>
  )
}


function ComingSoon({ what }: { what: string }) {
  return (
    <section>
      <h2>{what}</h2>
      <p>Coming soon.</p>
    </section>
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