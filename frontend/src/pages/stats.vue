<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h1>Stats</h1>
      </v-col>
      <v-spacer></v-spacer>
      <v-col>
        <v-autocomplete
          v-model="user"
          :items="users"
          item-value="id"
          item-title="first_name"
          label="Filter by user"
          return-object
          clearable
        >
          <template #item="{ item, props }">
            <v-list-item
              v-bind="props"
              :title="item.raw.first_name + ' ' + item.raw.last_name"
              :subtitle="item.raw.email"
            >
            </v-list-item>
          </template>
          <template #selection="{ item }">
            {{ item.raw.first_name }} {{ item.raw.last_name }}
          </template>
        </v-autocomplete>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <h2>Overall stats</h2>
      </v-col>
    </v-row>
    <v-row v-if="allStats">
      <v-col v-bind="colSizes">
        <v-card
          height="100%"
          elevation="4"
          min-height="280"
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
        v-if="allStats.total && allStats.duration"
        v-bind="colSizes"
      >
        <StatsCard
          title="Duration"
          :stats="allStats.duration"
          unit="Seconds"
        />
      </v-col>
      <v-col
        v-if="allStats.total && allStats.file_size"
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
        v-if="allStats.total && allStats.used_memory"
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
        <BarChart
          v-if="timeChartData"
          :options="{ responsive: true }"
          :data="timeChartData"
        />
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <h2>Validations composition</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <SplitStatsVisualization :user="user ?? undefined" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { getStats, getTimeStats } from "@/lib/http/validation"
import { formatInteger } from "@/lib/formatting"
import {
  Stats,
  TimeStats,
  severityLevelColorMap,
  SeverityLevel,
  StoredUser,
} from "@/lib/definitions/api"

import { fetchUsers } from "@/lib/http/users"

import Color from "color"

// display
const colSizes = {
  cols: 12,
  xs: 12,
  sm: 6,
  md: 4,
  lg: 3,
  xl: 2,
}

const user = ref<StoredUser | null>(null)
const users = ref<StoredUser[]>([])

async function loadUsers() {
  users.value = await fetchUsers()
}

// basic stats cards
const allStats = ref<Stats>()

async function loadStats() {
  allStats.value = await getStats(user.value ?? undefined)
}

// chart in time
const timeStats = ref<TimeStats>()

async function loadTimeStats() {
  timeStats.value = await getTimeStats(user.value ?? undefined)
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

watch(user, () => {
  loadStats()
  loadTimeStats()
})

onMounted(() => {
  loadUsers()
  loadStats()
  loadTimeStats()
})
</script>

<style scoped></style>
