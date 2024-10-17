import { Credentials, Validation, ValidationDetail } from "../definitions/api"
import { FUpload } from "../definitions/upload"
import { jsonFetch, wrapFetch } from "./util"

export const urls = {
  list: "validations/validation/",
  file: "validations/validation/file/",
  sushi: "validations/validation/sushi/",
}

export async function getValidation(id: string) {
  const url = `${urls.list}${id}/`

  return jsonFetch<Validation>(url)
}

export async function getValidationDetail(id: string) {
  const url = `${urls.list}${id}/`

  return jsonFetch<ValidationDetail>(url)
}

export async function getValidations() {
  return jsonFetch<Validation[]>(urls.list)
}

export async function validateFile(file: FUpload) {
  // we need to send the data in a multipart form
  const form = new FormData()
  form.append("file", file.file)

  if (typeof file.platform === "string") {
    form.append("platform_name", file.platform)
  }
  else if (file.platform === undefined) {
    form.append("platform_name", "")
  }
  else {
    form.append("platform", file.platform.id)
  }

  return jsonFetch<Validation>(urls.file, {
    method: "POST",
    body: form,
  })
}

export async function validateSushi(credentials: Credentials) {
  return wrapFetch(urls.sushi, {
    method: "POST",
    json: credentials,
  })
}
