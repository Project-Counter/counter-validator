export function required(val: unknown) {
  return !!val || "This field is required"
}

export function email(val: string) {
  const re =
    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  return re.test(String(val).toLowerCase()) || "Invalid email address"
}

export function password(val: string) {
  return val.length >= 8 || "Password must be at least 8 characters long"
}
