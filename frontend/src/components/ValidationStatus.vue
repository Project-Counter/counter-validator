<template>
  <v-tooltip v-if="!validation">
    <template #activator="{ props }">
      <v-icon
        v-bind="props"
        color="grey"
        icon="mdi-question"
      />
    </template>
    Unknown
  </v-tooltip>

  <v-tooltip v-else-if="validation.status == Status.WAITING">
    <template #activator="{ props }">
      <v-icon
        v-bind="props"
        color="grey"
        icon="mdi-clock"
      />
    </template>
    Waiting
  </v-tooltip>

  <v-tooltip v-else-if="validation.status == Status.RUNNING">
    <template #activator="{ props }">
      <v-progress-circular
        v-bind="props"
        color="grey"
        indeterminate
        :size="18"
      />
    </template>
    Running
  </v-tooltip>

  <v-tooltip v-else-if="validation.status == Status.SUCCESS">
    <template #activator="{ props }">
      <v-icon
        v-bind="props"
        color="grey"
        icon="mdi-check"
      />
    </template>
    Finished successfully
  </v-tooltip>

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
