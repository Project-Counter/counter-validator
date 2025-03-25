<template>
  <v-skeleton-loader
    v-if="isLoading"
    type="article"
  ></v-skeleton-loader>
  <div
    v-else-if="isError"
    class="error"
  >
    <v-icon
      class="me-2"
      size="large"
      color="grey-darken-1"
      >mdi-emoticon-sad-outline</v-icon
    >
    Failed to fetch changelog
  </div>
  <div v-else>
    <div
      v-for="entry in entries"
      :key="entry.version"
      class="changelog-entry"
    >
      <h3 class="text-h5">
        {{ entry.version }}
        <span class="text-h6 font-weight-light ms-2">{{ entry.date }}</span>
      </h3>

      <div v-html="mdToHtml(entry.markdown)"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from "marked"
import DOMPurify from "dompurify"
import { useAppStore } from "@/stores/app"

const entries = ref<{ version: string; date: string; markdown: string }[]>([])
const store = useAppStore()
const isLoading = ref(false)
const isError = ref(false)

function mdToHtml(md: string) {
  const renderer = new marked.Renderer()
  renderer.link = ({ href, title, text }) =>
    `<a target="_blank" href="${href}" title="${title}">${text}</a>`

  let html = marked.parse(md, {
    breaks: false,
    gfm: true,
    renderer: renderer,
    async: false,
  })
  return DOMPurify.sanitize(html)
}

onMounted(async () => {
  isLoading.value = true
  const res = await fetch("/api/v1/core/changelog")
  if (!res.ok) {
    store.displayNotification({
      message: "Failed to fetch changelog",
      type: "error",
    })
    isLoading.value = false
    isError.value = true
    return
  }
  entries.value = await res.json()
  isLoading.value = false
})
</script>

<style lang="scss">
.changelog-entry {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: solid 1px #ccc;
  &:first-child {
    padding-top: 0;
    margin-top: 0;
    border-top: none;
  }

  h2 {
    padding: 1rem 0 0.25rem 0.75rem;
    color: #444;
    font-size: 1.35rem;
  }
  h3 {
    padding: 0.75rem 0 0.25rem 1.5rem;
    color: #444;
  }
  h4 {
    padding: 0.5rem 0 0.125rem 2.5rem;
    color: #444;
  }
  ul {
    color: #555;
    padding-left: 4.5rem;
  }
}
</style>
