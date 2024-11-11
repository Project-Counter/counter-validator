<template>
  <span>{{ format(date, "yyyy-mm-dd") }}</span>
  <span class="text-caption ps-1">{{ format(date, "HH:MM:SS") }}</span>
</template>

<script setup lang="ts">
import { format } from "date-fns/format"

const props = defineProps<{
  dateString: string
}>()

// computed
const date = computed(() => {
  return new Date(props.dateString)
})
</script>

<style scoped></style>
