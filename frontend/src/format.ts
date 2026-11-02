export function gold(amount: number): string {
  return `${(amount / 1000).toLocaleString()}k`
}

export function target(value: number): string {
  return value > 0 ? `${value}+` : '-'
}
