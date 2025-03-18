import { defineStore } from "pinia"
import type { SystemInfo, User } from "@/lib/definitions/api"
import { VueError } from "@/lib/definitions/VueError"
import { useStorage } from "@vueuse/core"
import { Notification } from "@/lib/definitions/notifications"
import { fetchSystemInfo } from "@/lib/http/auth"

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

  // system info
  const systemInfo = ref<SystemInfo | null>(null)
  async function updateSystemInfo() {
    systemInfo.value = await fetchSystemInfo()
  }

  const isUserRegistrationAllowed = computed<boolean>(() => {
    return systemInfo.value?.ALLOW_USER_REGISTRATION || false
  })

  onMounted(async () => {
    await updateSystemInfo()
  })

  return {
    user,
    userVerified,
    errors,
    darkTheme,
    notification,
    showNotification,
    displayNotification,
    systemInfo,
    updateSystemInfo,
    isUserRegistrationAllowed,
  }
})
