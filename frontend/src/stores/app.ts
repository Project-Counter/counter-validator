import { defineStore } from "pinia"
import type { User } from "@/lib/definitions/api"
import { VueError } from "@/lib/definitions/VueError"
import { useStorage } from "@vueuse/core"
import { ValidatedFile } from "@/lib/definitions/upload"
import { Notification } from "@/lib/definitions/notifications"

export const useAppStore = defineStore("app", () => {
  const user: Ref<User> = ref({
    first_name: "",
    last_name: "",
    email: "",
  })
  const loggedIn: Ref<boolean | null> = ref(null)

  const errors: Ref<VueError[]> = ref([])

  const notification = ref<Notification | null>(null)
  const showNotification = ref(false)
  watch(showNotification, (value) => {
    notification.value = value ? notification.value : null
  })

  const darkTheme = useStorage("pinia/dark-theme", false)

  const fileHistory = useStorage<ValidatedFile[]>("pinia/file-history", [])

  function displayNotification(n: Notification) {
    notification.value = n
    showNotification.value = true
  }

  return {
    user,
    loggedIn,
    errors,
    darkTheme,
    fileHistory,
    notification,
    showNotification,
    displayNotification,
  }
})
