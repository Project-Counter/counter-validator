import type { Platform, Status, ValidationBase } from "@/lib/definitions/api"

export type FUpload = {
  file: File
  err?: string
  platform?: string | Platform
}

export type ValidatedFile = {
  filename: string
  id?: string // uuid
  status?: Status
} & ValidationBase
