import { useState } from 'react'
import { Link, useParams } from 'react-router'
import { type League, type Member, type Season, type User } from './api.ts'
import CommissionerPanel from './CommissionerPanel.tsx'
import CreateSeasonForm from './CreateSeasonForm.tsx'
import { useApi } from './useApi.ts'

type Props = {
  user: User
}

export default function LeaguePage({ user }: Props) {
  const { leagueId } = useParams()
  const [reloads, setReloads] = useState(0)
  const league = useApi<League>(`/leagues/${leagueId}`)
  const seasons = useApi<Season[]>(`/leagues/${leagueId}/seasons`, reloads)
  const members = useApi<Member[]>(`/leagues/${leagueId}/members`, reloads)

  if (league.error) {
    return (
      <section>
        <p role="alert">{league.error}</p>
        <Link to="/leagues">Back to my leagues</Link>
      </section>
    )
  }
  if (!league.data) {
    return <p>Loading…</p>
  }
  const isOwner = league.data.owner.id === user.id

  function reload() {
    setReloads((count) => count + 1)
  }

  return (
    <section>
      <Link to="/leagues">← My leagues</Link>
      <h2>{league.data.name}</h2>
      <p>Run by {league.data.owner.display_name}</p>

      <h3>Seasons</h3>
      {seasons.error && <p role="alert">{seasons.error}</p>}
      {seasons.data?.length === 0 && <p>No seasons yet.</p>}
      <ul>
        {seasons.data?.map((season) => (
          <li key={season.id}>
            <Link to={`/seasons/${season.id}`}>{season.name}</Link> ({season.format})
            {season.is_active ? '' : ' — finished'}
          </li>
        ))}
      </ul>
      {isOwner && <CreateSeasonForm leagueId={league.data.id} onCreated={reload} />}
      <h3>Members</h3>
      {members.error && <p role="alert">{members.error}</p>}
      <ul>
        {members.data?.map((member) => (
          <li key={member.user.id}>{member.user.display_name}</li>
        ))}
      </ul>
      {isOwner && <CommissionerPanel leagueId={league.data.id} onMembersChanged={reload} />}
    </section>
  )
}
