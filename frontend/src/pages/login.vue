<template>
  <LoginPage v-if="!store.user?.id" />
</template>

<script setup lang="ts">
import { useAppStore } from "@/stores/app"

const store = useAppStore()
const router = useRouter()

async function goHome() {
  await router.push("/validation/")
}

watch(
  () => store.user,
  () => {
    if (store.user?.id) {
      goHome()
    }
  },
)
</script>

<style scoped></style>

<route>
meta:
  requiresAuth: false
</route>
