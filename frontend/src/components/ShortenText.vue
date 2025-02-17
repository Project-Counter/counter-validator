<template>
  <v-tooltip
    v-if="isClamped"
    bottom
    max-width="600px"
  >
    <template #activator="{ props }">
      <span v-bind="props">{{ clampedText }}&hellip;</span>
    </template>
    {{ text }}
  </v-tooltip>
  <span v-else>{{ text }}</span>
</template>

<script setup lang="ts">
const p = withDefaults(defineProps<{ text: string; length?: number; tolerance?: number }>(), {
  length: 60,
  tolerance: 3,
})

const clampedText = ref<string | null>(null)
const isClamped = ref<boolean>(false)

function recompute() {
  if (p.text.length > p.length + p.tolerance) {
    clampedText.value = p.text.substring(0, p.length)
    isClamped.value = true
  } else {
    clampedText.value = null
    isClamped.value = false
  }
}

onMounted(() => {
  recompute()
})
</script>
