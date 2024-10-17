import { defineStore } from "pinia"
import type { User } from "@/lib/definitions/api"
import { VueError } from "@/lib/definitions/VueError"
import { useStorage } from "@vueuse/core"
import { ValidatedFile } from "@/lib/definitions/upload"

export const useAppStore = defineStore("app", () => {
  const user: Ref<User> = ref({
    first_name: "",
    last_name: "",
    email: "",
  })
  const loggedIn: Ref<boolean | null> = ref(null)

  const errors: Ref<VueError[]> = ref([])

  const darkTheme = useStorage("pinia/dark-theme", false)

  const fileHistory = useStorage<ValidatedFile[]>("pinia/file-history", [])

  return {
    user,
    loggedIn,
    errors,
    darkTheme,
    fileHistory,
  }
})
