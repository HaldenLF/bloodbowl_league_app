import { useEffect, useState } from 'react'
import { api } from './api.ts'

type Result<T> = {
  key: string
  data?: T
  error?: string
}

export function useApi<T>(path: string, reloadKey = 0) {
  const key = `${path}#${reloadKey}`
  const [result, setResult] = useState<Result<T> | null>(null)

  useEffect(() => {
    let cancelled = false
    api<T>(path)
      .then((data) => {
        if (!cancelled) setResult({ key, data })
      })
      .catch((err: unknown) => {
        if (!cancelled) setResult({ key, error: err instanceof Error ? err.message : 'Something went wrong' })
      })
    return () => {
      cancelled = true
    }
  }, [key, path])

  const current = result?.key === key ? result : null
  return { data: current?.data ?? null, error: current?.error ?? null, loading: current === null }
}
