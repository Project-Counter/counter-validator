import { defineStore } from "pinia"
import type { User } from "@/lib/definitions/User"
import { VueError } from "@/lib/definitions/VueError"

export const useAppStore = defineStore("app", () => {
	const user: Ref<User> = ref({
		first_name: "",
		last_name: "",
		email: "",
	})
	const loggedIn: Ref<boolean | null> = ref(null)

	const errors: Ref<VueError[]> = ref([])

	return {
		user,
		loggedIn,
		errors,
	}
})
