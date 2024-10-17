export type ApiKey = {
  prefix: string
  created: string
  name: string
  revoked: boolean
  expiry_date: string
  has_expired: boolean
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

export type Message = {
  l: string // level
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

export type Validation = {
  id: number
  api_key?: number
  status: Status
  created: string
  filename?: string
  platform: string
  platform_name: string
}

export type ValidationDetail = Validation & {
  result: Result
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
