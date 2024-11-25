<template>
  <div class="d-flex">
    <MonthPicker
      v-model="start"
      label="Start"
      :validator="startValidator"
      class="pr-6"
    />
    <MonthPicker
      v-model="end"
      label="End"
      :validator="endValidator"
    />
  </div>
</template>

<script setup lang="ts">
const start = defineModel<Date>("start", { required: true })
const end = defineModel<Date>("end", { required: true })

function endValidator(value: Date): boolean {
  return start.value <= value
}

function startValidator(value: Date): boolean {
  return value <= end.value
}
</script>

<style scoped></style>
