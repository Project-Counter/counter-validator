<template>
  <span>
    <v-tooltip
      v-for="[level, value] in statEntries"
      :key="level"
    >
      <template #activator="{ props }">
        <span
          v-bind="props"
          :class="'text-' + levelColorMap.get(level)"
          class="me-3 text-caption"
        >
          <v-icon
            :icon="'mdi-' + levelIconMap.get(level)"
            size="x-small"
          />{{ value }}
        </span>
      </template>
      <span>{{ level }}</span>
    </v-tooltip>
  </span>
</template>

<script setup lang="ts">
import { defineProps } from "vue"
import { ValidationCore, levelColorMap, levelIconMap } from "@/lib/definitions/api"
import type { Entries } from "type-fest"

let p = defineProps<{
  item: ValidationCore
}>()

const statEntries = computed(() => Object.entries(p.item.stats) as Entries<typeof p.item.stats>)
</script>

<style scoped></style>
