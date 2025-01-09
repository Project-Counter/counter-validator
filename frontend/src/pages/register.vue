<template>
  <LoginPage
    v-if="!store.user?.id"
    :initial-page="LoginSubPage.Signup"
  />
</template>

<script setup lang="ts">
import { useAppStore } from "@/stores/app"
import { LoginSubPage } from "@/lib/login"

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
