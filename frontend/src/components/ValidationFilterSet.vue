<template>
  <v-row>
    <v-col
      cols="12"
      sm="6"
      md="4"
      lg="2"
      xl="2"
    >
      <v-select
        v-model="sourceFilter"
        :items="dataSources"
        label="Data source"
        multiple
        clearable
      />
    </v-col>

    <v-col
      cols="12"
      sm="6"
      md="5"
      lg="3"
      xxl="2"
    >
      <v-select
        v-model="validationResultFilter"
        :items="severityLevels"
        label="Validation result"
        multiple
        clearable
      >
        <template #selection="{ item }">
          <v-icon
            size="x-small"
            class="mr-1"
            :color="severityLevelColorMap.get(item.value)"
          >
            mdi-{{ severityLevelIconMap.get(item.value) }}
          </v-icon>
          {{ item.title }}
        </template>
      </v-select>
    </v-col>

    <v-col
      cols="12"
      :sm="true"
      md="3"
      lg="2"
      xxl="1"
    >
      <v-select
        v-model="copVersionFilter"
        :items="copVersions"
        label="CoP version"
        multiple
        clearable
      />
    </v-col>

    <v-col
      cols="12"
      sm="5"
      md="4"
      lg="3"
      xl="2"
    >
      <v-select
        v-model="endpointFilter"
        :items="counterAPIEndpoints"
        label="Endpoint"
        multiple
        clearable
      />
    </v-col>

    <v-col
      cols="12"
      :sm="true"
      md="3"
      lg="2"
      xl="2"
      xxl="1"
    >
      <v-select
        v-model="reportCodeFilter"
        :items="reportCodes"
        label="Report code"
        multiple
        clearable
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { CoP, copVersions, counterAPIEndpoints, ReportCode } from "@/lib/definitions/counter"
import {
  CounterAPIEndpoint,
  DataSource,
  dataSources as dataSourcesRaw,
  SeverityLevel,
  severityLevelColorMap,
  severityLevelIconMap,
} from "@/lib/definitions/api"

const validationResultFilter = defineModel<SeverityLevel[]>("validationResultFilter")
const copVersionFilter = defineModel<CoP[]>("copVersionFilter")
const reportCodeFilter = defineModel<ReportCode[]>("reportCodeFilter")
const endpointFilter = defineModel<CounterAPIEndpoint[]>("endpointFilter")
const sourceFilter = defineModel<DataSource[]>("sourceFilter")

// filters
const severityLevels = [
  ...severityLevelIconMap.keys().map((k) => ({
    value: k,
    title: k,
    props: {
      "append-icon": "mdi-" + severityLevelIconMap.get(k),
      "base-color": severityLevelColorMap.get(k),
    },
  })),
]

const dataSources = dataSourcesRaw.map((ds) => {
  return {
    value: ds,
    title: ds === "file" ? "File" : "COUNTER API",
    props: {
      "append-icon": ds === "file" ? "mdi-file-outline" : "mdi-cloud-outline",
    },
  }
})

const reportCodes = Object.values(ReportCode)
</script>

<style scoped></style>
