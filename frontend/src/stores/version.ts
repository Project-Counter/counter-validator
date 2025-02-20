import { defineStore } from "pinia"
import { jsonFetch } from "@/lib/http/util"
import { compareVersions } from "compare-versions"

export const useVersionStore = defineStore("version", () => {
  // server version
  const server = ref<string>("")
  const upstream = ref<string>("")
  const upToDate = computed<boolean | null>(() => {
    if (server.value && upstream.value) {
      return compareVersions(server.value, upstream.value) >= 0
    }
    // we don't know yet
    return null
  })

  async function update() {
    const reply = await jsonFetch<{ server: string; upstream: string }>("core/version")
    server.value = reply.server
    upstream.value = reply.upstream
  }

  return {
    server,
    upstream,
    upToDate,
    update,
  }
})
