<template>
  <v-tooltip :text="dateHuman">
    <template #activator="{ props }">
      <span v-bind="props">{{ relative }}</span>
    </template>
  </v-tooltip>
</template>

<script setup lang="ts">
import { intlFormatDistance } from "date-fns"

const p = defineProps<{
  date: string
}>()

const relative = computed(() => {
  try {
    return intlFormatDistance(p.date, Date.now())
  } catch {
    return "N/A"
  }
})

const dateHuman = computed(() => {
  try {
    return new Date(p.date).toLocaleString()
  } catch {
    return "N/A"
  }
})
</script>
