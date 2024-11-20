export type Notification = {
  type: "error" | "warning" | "info" | "success"
  message: string
  timeout?: number
}
