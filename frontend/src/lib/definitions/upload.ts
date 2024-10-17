import type { ValidationBase, Status, Platform } from "@/lib/definitions/api"

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
