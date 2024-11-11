<template>
  <v-icon
    v-if="!validation"
    color="grey"
    icon="mdi-question"
  />
  <v-icon
    v-else-if="validation.status == Status.WAITING"
    color="grey"
    icon="mdi-clock"
  />
  <v-progress-circular
    v-else-if="validation.status == Status.RUNNING"
    color="grey"
    indeterminate
    :size="18"
  />
  <v-icon
    v-else-if="validation.status == Status.SUCCESS"
    color="success"
    icon="mdi-check"
  />
  <v-tooltip v-else>
    <template #activator="{ props }">
      <v-icon
        color="error"
        icon="mdi-alert"
        v-bind="props"
      />
    </template>
    <div><strong>Error message</strong>: {{ validation.error_message }}</div>
  </v-tooltip>
</template>

<script setup lang="ts">
import { Status, ValidationBase } from "@/lib/definitions/api"

defineProps<{
  validation?: ValidationBase
}>()
</script>
