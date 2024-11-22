<template>
  <v-chip
    v-if="severity"
    :color="severityLevelColorMap.get(severity)"
    :variant="variant"
  >
    <v-icon class="mr-1">mdi-{{ severityLevelIconMap.get(severity) }}</v-icon>
    {{ severity }}
  </v-chip>
</template>

<script setup lang="ts">
import { severityLevelColorMap, SeverityLevel, severityLevelIconMap } from "@/lib/definitions/api"

withDefaults(
  defineProps<{
    severity: SeverityLevel
    variant?: "flat" | "text" | "elevated" | "tonal" | "outlined" | "plain"
  }>(),
  {
    variant: "tonal",
  },
)
</script>
