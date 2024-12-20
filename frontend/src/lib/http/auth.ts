import { useAppStore } from "@/stores/app"
import { HttpStatusError, jsonFetch, wrapFetch } from "./util"
import { ApiKey, User } from "../definitions/api"

export const urls = {
  user: "core/me",
  login: "auth/login/",
  logout: "auth/logout/",
  signup: "auth/registration/",
  apiKey: "core/api-key/",
}

export async function checkUser(reset = false) {
  const store = useAppStore()
  if (reset) {
    store.loggedIn = null
  }

  try {
    store.user = await jsonFetch<User>(urls.user)
  } catch (err: unknown) {
    store.loggedIn = false
    if (err instanceof HttpStatusError) {
      if (![401, 403].includes(err?.res?.status)) {
        // TODO: 500 -> show error instead of login  // eslint-disable-line
      }
    }
    return
  }
  store.loggedIn = true
}

export async function updateUser(obj: User) {
  try {
    await wrapFetch(urls.user, {
      method: "PATCH",
      json: obj,
    })
  } finally {
    await checkUser()
  }
}

export async function login(email: string, password: string) {
  try {
    await wrapFetch(urls.login, {
      method: "POST",
      json: { email, password },
    })
  } finally {
    await checkUser()
  }
}

export async function logout() {
  try {
    await wrapFetch(urls.logout, {
      method: "POST",
    })
  } finally {
    await checkUser(true)
  }
}

export async function signup(email: string, password1: string, password2: string) {
  try {
    await wrapFetch(urls.signup, {
      method: "POST",
      json: { email, password1, password2 },
    })
  } finally {
    await checkUser()
  }
}

export async function loadApiKeys() {
  return jsonFetch<ApiKey[]>(urls.apiKey)
}

export async function createApiKey(name: string, expiryDate: Date | null) {
  // the post reply is not a serialized key, but just an object
  // with the new key as a string
  return jsonFetch<{ key: string }>(urls.apiKey, {
    method: "POST",
    json: { name, expiry_date: expiryDate },
  })
}

export async function revokeApiKey(prefix: string) {
  return jsonFetch(urls.apiKey + prefix + "/", {
    method: "DELETE",
  })
}
