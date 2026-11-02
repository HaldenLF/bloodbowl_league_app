import { useEffect, useState } from 'react'
import { api } from './api.ts'

type Result<T> = {
  path: string
  key: string
  data?: T
  error?: string
}

export function useApi<T>(path: string | null, reloadKey = 0) {
  const key = `${path}#${reloadKey}`
  const [result, setResult] = useState<Result<T> | null>(null)

  useEffect(() => {
    if (path === null) return
    let cancelled = false
    api<T>(path)
      .then((data) => {
        if (!cancelled) setResult({ path, key, data })
      })
      .catch((err: unknown) => {
        if (!cancelled) setResult({ path, key, error: err instanceof Error ? err.message : 'Something went wrong' })
      })
    return () => {
      cancelled = true
    }
  }, [key, path])

  const samePath = result?.path === path ? result : null
  const current = samePath?.key === key ? samePath : null
  return {
    data: samePath?.data ?? null,
    error: current?.error ?? null,
    loading: path !== null && current === null,
  }
}
