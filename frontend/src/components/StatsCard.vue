<template>
  <v-card
    :color="color"
    elevation="4"
  >
    <v-card-title v-if="title">
      <v-icon v-if="icon">{{ icon }}</v-icon>
      <span>{{ title }}</span>
      <span class="text-caption float-right pt-1">{{ unit }}</span>
    </v-card-title>
    <v-card-text class="text-center pt-2 pb-8">
      <div>
        <div class="text-caption">Min</div>
        <div
          class="text-green-darken-4"
          :class="numSizeClass"
        >
          {{ formattedStats.min }}
        </div>
      </div>
      <div v-if="stats.median">
        <div class="text-caption">Median</div>
        <div
          class="text-blue-darken-4"
          :class="numSizeClass"
        >
          {{ formattedStats.median }}
        </div>
      </div>
      <div>
        <div class="text-caption">Avg</div>
        <div
          class="text-indigo-darken-4"
          :class="numSizeClass"
        >
          {{ formattedStats.avg }}
        </div>
      </div>
      <div>
        <div class="text-caption">Max</div>
        <div
          class="text-red-darken-4"
          :class="numSizeClass"
        >
          {{ formattedStats.max }}
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { MinMaxStats } from "@/lib/definitions/api"
import { filesize } from "filesize"

const props = withDefaults(
  defineProps<{
    title?: string
    unit?: string
    stats: MinMaxStats
    icon?: string
    color?: string
    format?: "float" | "int" | "percent" | "fileSize"
  }>(),
  { format: "float", title: "", unit: "", icon: "", color: "white" },
)

const numSizeClass = "text-h5"

const formattedStats = computed(() => {
  return {
    min: formatNumber(props.stats.min),
    max: formatNumber(props.stats.max),
    avg: formatNumber(props.stats.avg),
    median: props.stats.median ? formatNumber(props.stats.median) : undefined,
  }
})

function formatNumber(num: number) {
  switch (props.format) {
    case "int":
      return Math.round(num).toString()
    case "percent":
      return (num * 100).toFixed(2) + "%"
    case "fileSize":
      return filesize(num)
    default:
      return num.toFixed(2)
  }
}
</script>

<style scoped></style>
