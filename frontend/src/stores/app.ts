import { defineStore } from "pinia"
import type { User } from "@/lib/definitions/api"
import { VueError } from "@/lib/definitions/VueError"
import { useStorage } from "@vueuse/core"
import { Notification } from "@/lib/definitions/notifications"

export const useAppStore = defineStore("app", () => {
  // user and auth
  const user = ref<User | null>(null)
  const userVerified = computed<boolean>(() => {
    return user.value?.verified_email || false
  })

  // theme
  const darkTheme = useStorage("pinia/dark-theme", false)

  // errors
  const errors: Ref<VueError[]> = ref([])

  // notifications
  const notification = ref<Notification | null>(null)
  const showNotification = ref(false)
  watch(showNotification, (value) => {
    notification.value = value ? notification.value : null
  })

  function displayNotification(n: Notification) {
    notification.value = n
    showNotification.value = true
  }

  return {
    user,
    userVerified,
    errors,
    darkTheme,
    notification,
    showNotification,
    displayNotification,
  }
})
