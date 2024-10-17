<template>
  <v-chip
    v-if="item && item.validation_result"
    :color="levelColorMap.get(item.validation_result)"
  >
    {{ item.validation_result }}
  </v-chip>
</template>

<script setup lang="ts">
import { levelColorMap } from "@/lib/definitions/api"

const p = defineProps<{
  item?: object
}>()

</script>
