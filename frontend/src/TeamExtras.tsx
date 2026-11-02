import { useState } from 'react'
import { postJson, type ShopItem } from './api.ts'
import { gold } from './format.ts'
import { useApi } from './useApi.ts'

const LABELS: Record<ShopItem['item'], string> = {
  re_roll: 'Re-rolls',
  assistant_coach: 'Assistant coaches',
  cheerleader: 'Cheerleaders',
  apothecary: 'Apothecary',
  dedicated_fan: 'Dedicated fans',
}

type Props = {
  teamId: number
  treasury: number
  canEdit: boolean
  reloadKey: number
  onBought: () => void
}

export default function TeamExtras({ teamId, treasury, canEdit, reloadKey, onBought }: Props) {
  const shop = useApi<ShopItem[]>(`/teams/${teamId}/shop`, reloadKey)
  const [busyItem, setBusyItem] = useState<ShopItem['item'] | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function buy(entry: ShopItem) {
    if (entry.price === null) return
    if (!window.confirm(`Buy 1 ${LABELS[entry.item].toLowerCase()} for ${gold(entry.price)}? There is no refund.`)) return
    setBusyItem(entry.item)
    setError(null)
    try {
      await postJson(`/teams/${teamId}/purchases`, { item: entry.item, quantity: 1 })
      onBought()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setBusyItem(null)
    }
  }

  function whyNot(entry: ShopItem): string | null {
    if (entry.unavailable_reason) return entry.unavailable_reason
    if (entry.owned >= entry.maximum) return 'Maximum reached'
    if (entry.price === null) return 'Not available for this race'
    if (entry.price > treasury) return 'Not enough gold'
    return null
  }

  return (
    <>
      <h3>Staff and extras</h3>
      {(error ?? shop.error) && <p role="alert">{error ?? shop.error}</p>}
      {!shop.data && !shop.error && <p>Loading…</p>}
      {shop.data && (
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Owned</th>
              <th>Price</th>
              {canEdit && <th />}
            </tr>
          </thead>
          <tbody>
            {shop.data.map((entry) => {
              const reason = whyNot(entry)
              return (
                <tr key={entry.item}>
                  <td>{LABELS[entry.item]}</td>
                  <td>
                    {entry.owned} / {entry.maximum}
                  </td>
                  <td>{entry.price === null ? '—' : gold(entry.price)}</td>
                  {canEdit && (
                    <td>
                      {reason ? (
                        <small>{reason}</small>
                      ) : (
                        <button type="button" disabled={busyItem !== null} onClick={() => void buy(entry)}>
                          {busyItem === entry.item ? 'Buying…' : 'Buy 1'}
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </>
  )
}
