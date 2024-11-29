<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>Stats</h2>
      </v-col>
    </v-row>
    <v-row v-if="allStats">
      <v-col
        v-if="allStats.total"
        v-bind="colSizes"
      >
        <v-card
          color="grey-lighten-3"
          height="100%"
        >
          <v-card-title>
            <span>Total validations</span>
          </v-card-title>
          <v-card-text class="text-center pt-2">
            <div class="text-h2 text-green-darken-4 pt-16">
              {{ formatInteger(allStats.total) }}
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col
        v-if="allStats.duration"
        v-bind="colSizes"
      >
        <StatsCard
          title="Duration"
          :stats="allStats.duration"
          unit="Seconds"
        />
      </v-col>
      <v-col
        v-if="allStats.file_size"
        v-bind="colSizes"
      >
        <StatsCard
          title="File size"
          :stats="allStats.file_size"
          unit="Bytes"
          format="fileSize"
        />
      </v-col>
      <v-col
        v-if="allStats.used_memory"
        v-bind="colSizes"
      >
        <StatsCard
          title="Used memory"
          :stats="allStats.used_memory"
          unit="Bytes"
          format="fileSize"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { getStats } from "@/lib/http/validation"
import { formatInteger } from "../lib/formatting"
import { Stats } from "@/lib/definitions/api"

// display
const colSizes = {
  cols: 12,
  xs: 12,
  sm: 6,
  md: 4,
  lg: 3,
  xl: 2,
}

const allStats = ref<Stats>()

async function loadStats() {
  allStats.value = await getStats()
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped></style>
