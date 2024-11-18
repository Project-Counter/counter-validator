import { formatISO } from "date-fns"

export function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export class Timer {
  protected timeoutId: number | undefined

  sleep(ms: number, clear: boolean = true) {
    if (clear) this.clear()
    return new Promise((resolve) => {
      this.timeoutId = setTimeout(resolve, ms)
    })
  }

  clear() {
    if (this.timeoutId) clearTimeout(this.timeoutId)
  }
}

export function isoDate(date: Date) {
  return formatISO(date, { representation: "date" })
}
