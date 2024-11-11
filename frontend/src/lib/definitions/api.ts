export type ApiKey = {
  prefix: string
  created: string
  name: string
  revoked: boolean
  expiry_date: string
  has_expired: boolean
  key?: string
}

export type User = {
  first_name: string
  last_name: string
  email: string
}

export type Report = {
  counter_release: string
  report_id: string
}

export type SeverityLevel =
  | "Passed"
  | "Notice"
  | "Warning"
  | "Error"
  | "Critical error"
  | "Fatal error"
  | ""

export type Message = {
  l: SeverityLevel // level
  s: string // summary
  m: string // message
  p: number // position
  d?: string // data
  h?: string // hint
}

export type Result = {
  datetime: string
  result: string
  header: Record<string, string>
  messages: Message[]
}

export enum Status {
  WAITING = 0,
  RUNNING = 1,
  SUCCESS = 2,
  FAILURE = 3,
}

export const statusMap = new Map<Status, string>([
  [Status.WAITING, "Waiting"],
  [Status.RUNNING, "Running"],
  [Status.SUCCESS, "Success"],
  [Status.FAILURE, "Failure"],
])

export type ValidationBase = {
  id: string // uuid
  cop_version: string
  report_code: string
  validation_result: SeverityLevel
  status: Status
  created: string
  platform: string
  platform_name: string
  error_message: string
}

export type ValidationCore = {
  file_size: number
  used_memory: number
  duration: number
  stats: Record<string, number>
} & ValidationBase

export type Validation = {
  api_key?: number
  filename?: string
  file_size: number
} & ValidationBase

export const levelColorMap = new Map<SeverityLevel, string>([
  ["Passed", "success"],
  ["Notice", "info"],
  ["Warning", "warning"],
  ["Error", "error"],
  ["Critical error", "error"],
  ["Fatal error", "error"],
])

export const levelIconMap = new Map<SeverityLevel, string>([
  ["Passed", "check"],
  ["Notice", "information-outline"],
  ["Warning", "alert"],
  ["Error", "alert-circle"],
  ["Critical error", "alert-circle"],
  ["Fatal error", "alert-circle"],
])

export type ValidationDetail = Validation & {
  result_data: Result
}

export type Credentials = {
  url: string
  platform?: string
  customer_id: string
  requestor_id?: string
  api_key?: string
}

export type Platform = {
  id: string
  name: string
  abbrev: string
  deprecated: boolean
}

export type PlatformDetail = Platform & {
  reports: Report[]
  content_provider_name: string
  website: string
  sushi_services: string[]
}

export type SushiService = {
  id: string
  counter_release: string
  url: string
  ip_address_authorization?: boolean
  api_key_required?: boolean
  platform_attr_required?: boolean
  requestor_id_required?: boolean
  deprecated: boolean
}
