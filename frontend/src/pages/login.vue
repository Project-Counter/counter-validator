<template>
  <LoginPage v-if="!store.user?.id" />
  <v-container
    v-else
    class="d-flex justify-center"
    style="padding-top: 33vh"
  >
    <v-btn
      color="primary"
      size="x-large"
      to="/validation/"
    >
      <v-icon class="me-2">mdi-file-multiple</v-icon>
      My Validations
    </v-btn>
  </v-container>
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
  { immediate: true },
)
</script>

<style scoped></style>

<route>
meta:
  requiresAuth: false
  layout: "public"
</route>
