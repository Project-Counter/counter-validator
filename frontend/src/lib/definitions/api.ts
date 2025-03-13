import { CoP, ReportCode } from "@/lib/definitions/counter"

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
  id?: number
  first_name: string
  last_name: string
  email: string
  is_validator_admin?: boolean
  is_superuser?: boolean
  is_active?: boolean
  has_admin_role?: boolean
  last_login?: string
  verified_email?: boolean
  date_joined?: string
  validations_total?: number
  validations_last_week?: number
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
  | "Unknown"

export const severityLevelColorMap = new Map<SeverityLevel, string>([
  ["Unknown", "#aaaaaa"],
  ["Passed", "#0fa40f"],
  ["Notice", "#0267b4"],
  ["Warning", "#fc6100"],
  ["Error", "#dd0000"],
  ["Critical error", "#aa0000"],
  ["Fatal error", "#8f0026"],
])

export const severityLevelIconMap = new Map<SeverityLevel, string>([
  ["Passed", "check"],
  ["Notice", "information-outline"],
  ["Warning", "alert"],
  ["Error", "alert-circle"],
  ["Critical error", "alert-circle"],
  ["Fatal error", "alert-circle"],
  ["Unknown", "help-circle"],
])

export type Message = {
  severity: SeverityLevel // level
  summary: string // summary
  message: string // message
  location: string // position
  data: string // data
  hint: string // hint
}

export type Result = {
  datetime: string
  result: string
  header: {
    begin_date: string
    cop_version: string
    created: string
    created_by: string
    end_date: string
    format: string
    institution_name: string
    report: Record<string, string>
    report_id: string
  }
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
  [Status.SUCCESS, "Finished"],
  [Status.FAILURE, "Failure"],
])

export type Credentials = {
  customer_id: string
  requestor_id?: string
  api_key?: string
  platform?: string
}

export type ValidationBase = {
  id: string // uuid
  cop_version: CoP
  report_code: string
  validation_result: SeverityLevel
  status: Status
  created: string
  expiration_date: string
  error_message: string
  stats: Record<SeverityLevel, number>
  user?: User
}

export type ValidationCore = {
  file_size: number
  used_memory: number
  duration: number
} & ValidationBase

export type DataSource = "counter_api" | "file"

export const dataSources: DataSource[] = ["counter_api", "file"]

export type Validation = {
  api_key?: number
  filename?: string
  file_url?: string
  file_size: number
  api_key_prefix: string
  data_source: "counter_api" | "file"
  credentials: Credentials | null
  url: string | null
  requested_cop_version: CoP | null
  requested_report_code: ReportCode | null
  api_endpoint: string | null
  requested_extra_attributes: { [key: string]: string } | null
  requested_begin_date: string | null
  requested_end_date: string | null
  use_short_dates: boolean
  public_id: string | null
  user_note: string | null
} & ValidationBase

export type ValidationDetail = Validation & {
  result_data: Result
}

export type Platform = {
  id: string
  name: string
  abbrev: string
  deprecated: boolean
}

export type SushiService = {
  id: string
  counter_release: CoP
  url: string
  ip_address_authorization?: boolean
  api_key_required?: boolean
  platform_attr_required?: boolean
  requestor_id_required?: boolean
  deprecated: boolean
}

export type PlatformDetail = Platform & {
  reports: Report[]
  content_provider_name: string
  website: string
  sushi_services: SushiService[]
}

export type CounterAPIEndpoint = "/reports/[id]" | "/reports" | "/status" | "/members"

export type MinMaxStats = {
  min: number
  max: number
  avg: number
  median?: number
}

export type Stats = {
  total: number
  duration: MinMaxStats
  file_size: MinMaxStats
  used_memory: MinMaxStats
}

type LevelToCount = Record<SeverityLevel, number>

export type TimeStats = (LevelToCount & {
  date: string
  total: number
})[]

export type SplitStatsRec = {
  source: string
  method: string
  validation_result: string
  count: number
}

export type SplitStats = SplitStatsRec[]

export type QueueInfo = {
  queued: number
  running: number
  workers: number
}
