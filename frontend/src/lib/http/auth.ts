import { useAppStore } from "@/stores/app"
import { wfetch } from "./util"
import { User } from "../definitions/User"

export const urls = {
	user: "user/",
	login: "login/",
	logout: "logout/",
	signup: "registration/",
	apiKey: "api-key/",
}

export async function checkUser(reset = false) {
	const store = useAppStore()
	if (reset) {
		store.loggedIn = null
	}

	try {
		store.user = await wfetch(urls.user)
	}
	catch (err) {
		store.loggedIn = false
		if (![401, 403].includes(err?.res?.status)) {
			// TODO: handling??
		}
		return
	}
	store.loggedIn = true
}

export async function updateUser(obj: User) {
	try {
		await wfetch(urls.user, {
			method: "PATCH",
			body: obj,
		})
	}
	finally {
		await checkUser()
	}
}

export async function login(email: string, password: string) {
	try {
		await wfetch(urls.login, {
			method: "POST",
			body: { email, password },
		})
	}
	finally {
		await checkUser()
	}
}

export async function logout() {
	try {
		await wfetch(urls.logout, {
			method: "POST",
		})
	}
	finally {
		await checkUser(true)
	}
}

export async function signup(email: string, password1: string, password2: string) {
	try {
		await wfetch(urls.signup, {
			method: "POST",
			body: { email, password1, password2 },
		})
	}
	finally {
		await checkUser()
	}
}

export async function loadApiKeys() {
	return wfetch(urls.apiKey)
}

export async function createApiKey(name: string, expiryDate: Date | null) {
	return wfetch(urls.apiKey, {
		method: "POST",
		body: { name, expiry_date: expiryDate },
	})
}

export async function revokeApiKey(prefix: string) {
	return wfetch(urls.apiKey + prefix + "/", {
		method: "DELETE",
	})
}
