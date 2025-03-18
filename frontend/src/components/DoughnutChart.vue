<template>
  <Doughnut
    :options="options"
    :data="props.data"
  />
</template>

<script setup lang="ts">
import { Doughnut } from "vue-chartjs"
import { ArcElement, Chart as ChartJS, ChartData, Colors, Legend, Title, Tooltip } from "chart.js"

ChartJS.register(Title, Tooltip, Legend, ArcElement, Colors)

const props = defineProps<{ data: ChartData<"doughnut">; title?: string }>()

const options = ref({
  responsive: true,
  plugins: {
    title: {
      text: props.title || "",
      display: !!props.title,
    },
  },
})
</script>

<style scoped></style>
