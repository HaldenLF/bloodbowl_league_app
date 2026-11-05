import { useState } from 'react'
import { Link, NavLink } from 'react-router'
import { type User } from './api.ts'

type Props = {
  user: User
  onLogOut: () => void
}

export default function TopBar({ user, onLogOut }: Props) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="topbar">
      <Link to="/" className="logo">
        <img src="/logo.svg" alt="Blood Bowl League home" width={40} height={40} />
      </Link>
      <nav aria-label="Main">
        <NavLink to="/teams">Teams</NavLink>
        <NavLink to="/leagues">Leagues</NavLink>
      </nav>
      <div className="burger">
        <button
          type="button"
          aria-label="Menu"
          aria-expanded={menuOpen}
          aria-controls="account-menu"
          onClick={() => setMenuOpen((open) => !open)}
        >
          ☰
        </button>
        {menuOpen && (
          <div id="account-menu" className="account-menu" onKeyDown={(e) => e.key === 'Escape' && setMenuOpen(false)}>
            <p>
              <strong>{user.display_name}</strong>
              <br />
              <small>{user.account_type}</small>
            </p>
            <button type="button" onClick={onLogOut}>
              Log out
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
