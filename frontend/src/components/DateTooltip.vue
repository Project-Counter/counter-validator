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
  date: string | null | undefined
}>()

const relative = computed(() => {
  if (!p.date) return "-"
  try {
    return intlFormatDistance(p.date, Date.now())
  } catch {
    return "N/A"
  }
})

const dateHuman = computed(() => {
  if (!p.date) return "Empty value"
  try {
    return new Date(p.date).toLocaleString()
  } catch {
    return "N/A"
  }
})
</script>
