<template>
  <v-alert
    v-if="!key"
    type="error"
  >
    Sorry, but the verification link is invalid. You may have copied only part of it, or it may have
    been corrupted during transmission. Please check the link and try again.
  </v-alert>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router"
import { verifyEmail } from "@/lib/http/auth"
import { useAppStore } from "@/stores/app"

const router = useRouter()
const route = useRoute()
const store = useAppStore()

const key = ref<string>(
  (Array.isArray(route.query.key) ? route.query.key[0] : route.query.key) || "",
)

onMounted(async () => {
  if (key.value) {
    try {
      await verifyEmail(key.value)
      store.displayNotification({
        message: "Email was successfully verified",
        type: "success",
      })
      await router.push("/validation/")
    } catch (e) {
      store.displayNotification({
        message: "Failed to verify email. Check the verification link.",
        type: "error",
      })
    }
  }
})
</script>

<style scoped></style>

<route>
meta:
  requiresAuth: false
</route>
