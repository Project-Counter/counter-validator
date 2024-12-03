<template>
  <div>
    <v-row>
      <v-col v-bind="colSizes">
        <DoughnutChart
          v-if="byResult"
          :data="byResult"
          title="By result"
        />
      </v-col>
      <v-col v-bind="colSizes">
        <DoughnutChart
          v-if="byCoP"
          :data="byCoP"
          title="By CoP"
        />
      </v-col>
      <v-col v-bind="colSizes">
        <DoughnutChart
          v-if="byReportCode"
          :data="byReportCode"
          title="By report code"
        />
      </v-col>
      <v-col v-bind="colSizes">
        <DoughnutChart
          v-if="byMethod"
          :data="byMethod"
          title="By method"
        />
      </v-col>
      <v-col v-bind="colSizes">
        <DoughnutChart
          v-if="bySource"
          :data="bySource"
          title="By source"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { severityLevelColorMap, SplitStats } from "@/lib/definitions/api"
import { getSplitStats } from "@/lib/http/validation"
import { ChartData } from "chart.js"
import { DataFrame } from "data-forge"

const stats = ref<SplitStats>([])
const df = ref<DataFrame>()

// display
const colSizes = {
  cols: 12,
  xs: 12,
  sm: 6,
  md: 4,
  lg: 3,
  xl: 2,
}

function byAttr(df: DataFrame, attr: string, colors: Record<string, string> | null = null) {
  if (!df) return
  const col = df
    .groupBy((row) => row[attr])
    .select((group) => ({
      [attr]: group.first()[attr],
      aggregation: group.deflate((row) => row.count).sum(),
    }))
    .toArray()

  let out: ChartData<"doughnut"> = {
    labels: col.map((row) => row[attr]),
    datasets: [
      {
        label: "Count",
        data: col.map((row) => row["aggregation"]),
      },
    ],
  }
  if (colors) {
    out.datasets[0].backgroundColor = col.map((row) => colors[row[attr]])
  }
  return out
}

// different slicings
const byMethod = ref()
const bySource = ref()
const byResult = ref()
const byCoP = ref()
const byReportCode = ref()

onMounted(async () => {
  stats.value = await getSplitStats()
  df.value = new DataFrame({
    values: stats.value,
  })
  byMethod.value = byAttr(df.value, "method")
  bySource.value = byAttr(df.value, "source")
  byResult.value = byAttr(df.value, "result", Object.fromEntries(severityLevelColorMap.entries()))
  byCoP.value = byAttr(df.value, "cop_version")
  byReportCode.value = byAttr(df.value, "report_code")
})
</script>

<style scoped></style>
