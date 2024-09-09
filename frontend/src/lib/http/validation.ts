import { ValidationFile } from "../definitions/ValidationFile"
import { wfetch } from "./util"

export const urls = {
	file: "validation/file/",
}

export async function validateFile(file: ValidationFile) {
	const params = new URLSearchParams()
	if (file.platform) {
		params.append("platform_name", file.platform)
	}
	// if (typeof file.platform === "string") {
	// 	params.append("platform_name", file.platform)
	// } else if (file.platform?.id) {
	// 	params.append("platform", file.platform?.id)
	// }
	return wfetch(urls.file + encodeURIComponent(file.file.name) + "/?" + params.toString(), {
		method: "POST",
		body: file.file,
	})
}
