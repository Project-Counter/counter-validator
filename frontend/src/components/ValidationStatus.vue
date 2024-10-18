<template>
  <template v-if="value == Status.WAITING">
    <v-icon
      color="grey"
      icon="mdi-clock"
    />
  </template>
  <template v-else-if="value == Status.RUNNING">
    <v-progress-circular
      color="grey"
      indeterminate
      :size="18"
    />
  </template>
  <template v-else-if="value == Status.SUCCESS">
    <v-icon
      color="success"
      icon="mdi-check"
    />
  </template>
  <template v-else>
    <v-icon
      color="error"
      icon="mdi-alert"
    />
  </template>
</template>

<script setup lang="ts">
import { Status } from "@/lib/definitions/api"

defineProps<{
  value?: Status
}>()
</script>
