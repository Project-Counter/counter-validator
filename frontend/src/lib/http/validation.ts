import { Credentials, Validation, ValidationDetail } from "../definitions/api"
import { FUpload } from "../definitions/upload"
import { jsonFetch, wrapFetch } from "./util"

export const urls = {
	list: "validation/",
	file: "validation/file/",
	sushi: "validation/sushi/",
}

export async function getValidation(id: string) {
	const url = `${urls.list}${id}/`

	return jsonFetch<Validation>(url)
}

export async function getValidationDetail(id: string) {
	const url = `${urls.list}${id}/details/`

	return jsonFetch<ValidationDetail>(url)
}

export async function getValidations() {
	return jsonFetch<Validation[]>(urls.list)
}

export async function validateFile(file: FUpload) {
	const params = new URLSearchParams()
	if (file.platform) {
		params.append("platform_name", file.platform)
	}
	return jsonFetch<Validation>(urls.file + encodeURIComponent(file.file.name) + "/?" + params.toString(), {
		method: "POST",
		body: file.file,
	})
}

export async function validateSushi(credentials: Credentials) {
	return wrapFetch(urls.sushi, {
		method: "POST",
		json: credentials,
	})
}
