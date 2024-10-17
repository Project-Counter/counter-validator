import type { ValidationBase, Status } from "@/lib/definitions/api"

export type FUpload = {
  file: File
  err?: string
  platform?: string
}

export type ValidatedFile = {
  filename: string
  id?: number
  status?: Status
} & ValidationBase
