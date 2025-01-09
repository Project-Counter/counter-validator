<template>
  <ValidationManagementWidget v-if="store.user?.id" />
</template>

<script setup lang="ts">
import { useAppStore } from "@/stores/app"
const store = useAppStore()
</script>
