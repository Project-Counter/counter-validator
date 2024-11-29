<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>Overall stats</h2>
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

    <v-row>
      <v-col>
        <h2>Time stats</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        lg="8"
        xl="6"
      >
        <Bar
          v-if="timeChartData"
          id="time-chart"
          :options="{ responsive: true }"
          :data="timeChartData"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { getStats, getTimeStats } from "@/lib/http/validation"
import { formatInteger } from "@/lib/formatting"
import { Stats, TimeStats, severityLevelColorMap, SeverityLevel } from "@/lib/definitions/api"
import { Bar } from "vue-chartjs"
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js"
import Color from "color"

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

// display
const colSizes = {
  cols: 12,
  xs: 12,
  sm: 6,
  md: 4,
  lg: 3,
  xl: 2,
}

// basic stats cards
const allStats = ref<Stats>()

async function loadStats() {
  allStats.value = await getStats()
}

// chart in time
const timeStats = ref<TimeStats>()

async function loadTimeStats() {
  timeStats.value = await getTimeStats()
}

const timeChartData = computed(() => {
  if (!timeStats.value) {
    return null
  }
  return {
    labels: timeStats.value.map((ts) => ts.date),
    datasets: [
      ...severityLevelColorMap.entries().map(([sl, color]: [SeverityLevel, string]) => {
        return {
          label: sl,
          backgroundColor: Color(color).alpha(0.6).rgb().string(),
          data: timeStats.value ? timeStats.value.map((ts) => ts[sl]) : [], // ? is a ts workaround
          stack: "Stack 0",
        }
      }),
    ],
  }
})

onMounted(() => {
  loadStats()
  loadTimeStats()
})
</script>

<style scoped></style>
