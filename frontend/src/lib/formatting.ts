import { formatISO } from "date-fns"

export function isoDate(date: Date) {
  return formatISO(date, { representation: "date" })
}

export function shortIsoDate(date: Date) {
  // returns just the year and month of the ISO date
  return formatISO(date, { representation: "date" }).slice(0, 7)
}

export function formatPercent(value: number, digits: number = 2) {
  return `${(value * 100).toFixed(digits)}%`
}

export function formatInteger(value: number) {
  return value.toLocaleString()
}
