import { useAppStore } from "@/stores/app"
import { HttpStatusError, jsonFetch, wrapFetch } from "./util"
import { ApiKey, User } from "../definitions/api"

export const urls = {
  user: "core/me",
  userPatch: "auth/user/",
  login: "auth/login/",
  logout: "auth/logout/",
  signup: "registration/",
  apiKey: "core/api-key/",
  requestReset: "auth/password/reset/",
  doReset: "auth/password/reset/confirm/",
  verifyEmail: "registration/verify-email/",
  resendVerificationEmail: "registration/resend-email/",
}

export async function checkUser() {
  const store = useAppStore()

  try {
    store.user = await jsonFetch<User>(urls.user)
  } catch (err: unknown) {
    if (err instanceof HttpStatusError) {
      if ([401, 403].includes(err?.res?.status)) {
        store.user = null
      }
    }
    return
  }
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
  await wrapFetch(urls.login, {
    method: "POST",
    json: { email, password },
  })
  await checkUser()
}

export async function logout() {
  try {
    await wrapFetch(urls.logout, {
      method: "POST",
    })
  } finally {
    await checkUser()
  }
}

export async function signup(
  email: string,
  password1: string,
  password2: string,
  extra: Record<string, string> = {},
) {
  await wrapFetch(urls.signup, {
    method: "POST",
    json: { email, password1, password2, ...extra },
  })
  await checkUser()
}

export async function requestPasswordReset(email: string) {
  return jsonFetch(urls.requestReset, {
    method: "POST",
    json: { email },
  })
}

export async function doPasswordReset(
  uid: string,
  token: string,
  new_password1: string,
  new_password2: string,
) {
  return jsonFetch<{ detail: string }>(urls.doReset, {
    method: "POST",
    json: { uid, token, new_password1, new_password2 },
  })
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

export async function verifyEmail(key: string) {
  await wrapFetch(urls.verifyEmail, {
    method: "POST",
    json: { key },
  })
}

export async function resendVerificationEmail(email: string) {
  await wrapFetch(urls.resendVerificationEmail, {
    method: "POST",
    json: { email },
  })
}
