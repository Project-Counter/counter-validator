<template>
  <v-tooltip :text="date">
    <template #activator="{ props }">
      <span v-bind="props">{{ relative }}</span>
    </template>
  </v-tooltip>
</template>

<script setup lang="ts">
import { intlFormatDistance } from "date-fns"

const p = defineProps({
	date: {
		type: String,
		required: true,
	},
})

const relative = computed(() => {
	try {
		return intlFormatDistance(p.date, Date.now())
	}
	catch {
		return "N/A"
	}
})
</script>
