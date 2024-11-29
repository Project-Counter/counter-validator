import {
  Credentials,
  Stats,
  Validation,
  ValidationCore,
  ValidationDetail,
} from "../definitions/api"
import { FUpload } from "../definitions/upload"
import { jsonFetch, wrapFetch } from "./util"
import { CoP, ReportCode } from "@/lib/definitions/counter"

import { isoDate } from "@/lib/formatting"

export const urls = {
  list: "validations/validation/",
  file: "validations/validation/file/",
  sushi: "validations/counter-api-validation/",
  coreList: "validations/validation-core/",
  stats: "validations/validation-core/stats/",
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

export async function getValidationCores() {
  return jsonFetch<ValidationCore[]>(urls.coreList)
}

export async function validateFile(file: FUpload) {
  // we need to send the data in a multipart form
  const form = new FormData()
  form.append("file", file.file)

  if (typeof file.platform === "string") {
    form.append("platform_name", file.platform)
  } else if (file.platform === undefined) {
    form.append("platform_name", "")
  } else {
    form.append("platform", file.platform.id)
  }

  return jsonFetch<Validation>(urls.file, {
    method: "POST",
    body: form,
  })
}

export async function validateCounterAPI(
  credentials: Credentials,
  url: string,
  cop: CoP,
  endpoint: string,
  reportCode?: ReportCode,
  beginDate?: Date,
  endDate?: Date,
  extraAttributes?: { [key: string]: string },
) {
  const data: {
    credentials: Credentials
    url: string
    cop_version: CoP
    api_endpoint: string
    report_code?: ReportCode
    begin_date?: string
    end_date?: string
    extra_attributes: { [key: string]: string } | undefined
  } = {
    credentials,
    url,
    cop_version: cop,
    api_endpoint: endpoint,
    extra_attributes: extraAttributes,
  }
  if (reportCode) {
    data["report_code"] = reportCode
  }
  if (beginDate) {
    data["begin_date"] = isoDate(beginDate)
  }
  if (endDate) {
    data["end_date"] = isoDate(endDate)
  }
  return wrapFetch(urls.sushi, {
    method: "POST",
    json: data,
  })
}

export async function deleteValidation(id: string) {
  return wrapFetch(`${urls.list}${id}/`, {
    method: "DELETE",
  })
}

export async function getStats(): Promise<Stats> {
  return jsonFetch<Stats>(urls.stats)
}
