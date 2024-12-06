import type { Status, ValidationBase } from "@/lib/definitions/api"

export type FUpload = {
  file: File
  err?: string
  user_note?: string
}

export type ValidatedFile = {
  filename: string
  id?: string // uuid
  status?: Status
} & ValidationBase
