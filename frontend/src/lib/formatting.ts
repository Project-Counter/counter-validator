import { formatISO } from "date-fns"

export function isoDate(date: Date) {
  return formatISO(date, { representation: "date" })
}

export function formatPercent(value: number, digits: number = 2) {
  return `${(value * 100).toFixed(digits)}%`
}

export function formatInteger(value: number) {
  return value.toLocaleString()
}
