<template>
  <Bar
    :options="options"
    :data="data"
  />
</template>

<script setup lang="ts">
import { Bar } from "vue-chartjs"

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ChartData,
} from "chart.js"

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

defineProps<{ data: ChartData; options: object }>()
</script>

<style scoped></style>
