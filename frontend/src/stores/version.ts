import { defineStore } from "pinia"
import { jsonFetch } from "@/lib/http/util"
import { compareVersions } from "compare-versions"

export const useVersionStore = defineStore("version", () => {
  // server version
  const server = ref<string>("")
  const upstream = ref<string>("")
  const upstreamUrl = ref<string>("")
  const frontend = import.meta.env.VITE_APP_VERSION
  const serverUpToDate = computed<boolean | null>(() => {
    if (server.value && upstream.value) {
      return compareVersions(server.value, upstream.value) >= 0
    }
    // we don't know yet
    return null
  })
  const frontEndUpToDate = computed<boolean | null>(() => {
    if (server.value) {
      return compareVersions(frontend, server.value) >= 0
    }
    // we don't know yet
    return null
  })

  async function update() {
    const reply = await jsonFetch<{ server: string; upstream: string; upstream_url: string }>(
      "core/version",
    )
    server.value = reply.server
    upstream.value = reply.upstream
    upstreamUrl.value = reply.upstream_url
  }

  return {
    server,
    upstream,
    upstreamUrl,
    serverUpToDate,
    update,
    frontend,
    frontEndUpToDate,
  }
})
