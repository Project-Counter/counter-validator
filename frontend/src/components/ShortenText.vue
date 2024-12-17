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
const props = withDefaults(defineProps<{ text: string; length?: number; tolerance?: number }>(), {
  length: 60,
  tolerance: 3,
})

const clampedText = ref<string | null>(null)
const isClamped = ref<boolean>(false)

function recompute() {
  if (props.text.length > props.length + props.tolerance) {
    clampedText.value = props.text.substring(0, props.length)
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
