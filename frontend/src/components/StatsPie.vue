<template>
  <span>
    <v-tooltip v-if="Object.keys(item.stats).length > 0">
      <template #activator="{ props }">
        <span v-bind="props">
          <SimplePie :parts="statParts" />
        </span>
      </template>
      <StatsTableSimple :stats="item.stats" />
    </v-tooltip>
  </span>
</template>

<script setup lang="ts">
import { defineProps } from "vue"
import { severityLevelColorMap, ValidationBase } from "@/lib/definitions/api"
import type { Entries } from "type-fest"
import StatsTableSimple from "@/components/StatsTableSimple.vue"

let p = defineProps<{
  item: ValidationBase
}>()

const statParts = computed(() =>
  (Object.entries(p.item.stats) as Entries<typeof p.item.stats>).map(([level, value]) => ({
    size: value,
    color: severityLevelColorMap.get(level) || "#aaaaaa",
  })),
)
</script>

<style scoped></style>
