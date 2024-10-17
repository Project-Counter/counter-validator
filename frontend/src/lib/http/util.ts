export function getCookie(key: string) {
  return document.cookie.split(";").find(row => row.trim().startsWith(key + "="))?.split("=")[1]
}

export type RequestOptions = undefined | (RequestInit & {
  json?: unknown
})

export class HttpStatusError extends Error {
  res

  constructor(res: Response) {
    super(`Response status: ${res.status}`)
    this.name = "HttpStatusError"
    this.res = res
  }
}

export class NoResponseError extends Error {}

export async function wrapFetch(resource: string, options: RequestOptions = undefined): Promise<Response> {
  if (!options) {
    options = {}
  }
  options.headers = new Headers(options.headers)
  options.mode = "same-origin"

  if (options.json) {
    options.body = JSON.stringify(options.json)

    options.headers.set("Content-Type", "application/json")
  }

  if (["POST", "PUT", "PATCH", "DELETE"].includes(options.method ?? "")) {
    const csrf = getCookie("csrftoken")
    if (csrf) {
      options.headers.set("X-CSRFToken", csrf)
    }
  }

  const res = await fetch("/api/" + resource, options)

  if (!res.ok) {
    const err = new HttpStatusError(res)
    throw err
  }

  return res
}

export async function jsonFetch<T>(resource: string, options: RequestOptions = undefined): Promise<T> {
  const res = await wrapFetch(resource, options)
  if (Number(res.headers.get("Content-Length")) == 0) {
    throw NoResponseError
  }
  return res.json() as Promise<T>
}
