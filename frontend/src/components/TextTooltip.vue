<template>
  <template v-if="text == tooltip || !tooltip">
    {{ text }}
  </template>
  <v-tooltip
    v-else
    :text="tooltip"
  >
    <template #activator="{ props }">
      <span v-bind="props">{{ text }}</span>
    </template>
  </v-tooltip>
</template>

<script setup lang="ts">
defineProps({
	text: {
		type: String,
		default: null,
	},
	tooltip: {
		type: String,
		default: null,
	},
})
</script>
