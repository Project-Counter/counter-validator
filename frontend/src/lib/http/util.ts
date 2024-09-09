export function getCookie(key: string) {
	return document.cookie.split(";").find(row => row.trim().startsWith(key + "="))?.split("=")[1]
}

// export interface RequestOptions extends RequestInit {
// 	body?: string,
// }

export class HttpStatusError extends Error {
	res

	constructor(res: Response) {
		super(`Response status: ${res.status}`)
		this.name = "HttpStatusError"
		this.res = res
	}
}

export async function wfetch(resource: string, options: RequestInit | undefined = undefined): Promise<unknown> {
	if (!options) {
		options = {}
	}
	options.headers = new Headers(options.headers)
	options.mode = "same-origin"

	if (options.body && !(options.body instanceof File)) {
		options.body = JSON.stringify(options.body)

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
	if (Number(res.headers.get("Content-Length")) > 0) {
		return res.json()
	}
}
