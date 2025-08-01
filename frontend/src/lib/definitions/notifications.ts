export type Notification = {
  type: "error" | "warning" | "info" | "success"
  message: string
  details?: string
  timeout?: number
}
