import { jsonFetch, wrapFetch } from "./util"
import { StoredUser, User } from "../definitions/api"

export const urls = {
  list: "core/user/",
}

export async function fetchUsers(): Promise<StoredUser[]> {
  return await jsonFetch<StoredUser[]>(urls.list, {
    method: "GET",
  })
}

export async function createUser(user: User) {
  return await jsonFetch<User>(urls.list, {
    method: "POST",
    json: user,
  })
}

export async function updateUser(user: User) {
  return await jsonFetch<User>(`${urls.list}${user.id}/`, {
    method: "PATCH",
    json: user,
  })
}

export async function deleteUser(user: User) {
  return await wrapFetch(`${urls.list}${user.id}/`, {
    method: "DELETE",
  })
}

export async function sendInvitationEmail(user: User) {
  return await jsonFetch(`${urls.list}${user.id}/send-invitation/`, {
    method: "POST",
  })
}
