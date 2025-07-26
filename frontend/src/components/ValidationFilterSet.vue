<template>
  <v-row>
    <v-col
      v-if="showPublishedFilter"
      cols="auto"
    >
      <v-select
        v-model="publishedFilter"
        :items="booleanOptions"
        label="Shared"
        hide-details
        min-width="8rem"
      />
    </v-col>

    <v-col cols="auto">
      <v-select
        v-model="sourceFilter"
        :items="dataSources"
        label="Data source"
        multiple
        clearable
        hide-details
        min-width="12rem"
      />
    </v-col>

    <v-col cols="auto">
      <v-select
        v-model="validationResultFilter"
        :items="severityLevels"
        label="Validation result"
        multiple
        clearable
        hide-details
        min-width="16rem"
        max-width="24rem"
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

    <v-col cols="auto">
      <v-select
        v-model="copVersionFilter"
        :items="copVersions"
        label="CoP version"
        multiple
        clearable
        hide-details
        min-width="10rem"
      />
    </v-col>

    <v-col cols="auto">
      <v-select
        v-model="endpointFilter"
        :items="counterAPIEndpoints"
        label="Endpoint"
        multiple
        clearable
        hide-details
        min-width="12rem"
      />
    </v-col>

    <v-col cols="auto">
      <v-select
        v-model="reportCodeFilter"
        :items="reportCodes"
        label="Report ID"
        multiple
        clearable
        hide-details
        min-width="10rem"
      />
    </v-col>

    <v-col cols="auto">
      <v-date-input
        v-model="dateFilter"
        label="Date"
        min-width="12rem"
        max-width="24rem"
        prepend-icon=""
        clearable
      />
    </v-col>

    <v-col v-if="showTextFilter">
      <v-text-field
        v-model="textFilter"
        :label="textFilterLabel"
        hide-details
        clearable
        append-inner-icon="mdi-magnify"
        min-width="12rem"
        max-width="24rem"
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { CoP, copVersions, counterAPIEndpoints, ReportCode } from "@/lib/definitions/counter"
import {
  CounterAPIEndpoint,
  DataSource,
  SeverityLevel,
  severityLevelColorMap,
  severityLevelIconMap,
} from "@/lib/definitions/api"
import { useValidationFilters } from "@/composables/validationFiltering"
import { booleanOptions } from "@/lib/options"
import { VDateInput } from "vuetify/labs/VDateInput"

// models
const validationResultFilter = defineModel<SeverityLevel[]>("validationResultFilter")
const copVersionFilter = defineModel<CoP[]>("copVersionFilter")
const reportCodeFilter = defineModel<ReportCode[]>("reportCodeFilter")
const endpointFilter = defineModel<CounterAPIEndpoint[]>("endpointFilter")
const sourceFilter = defineModel<DataSource[]>("sourceFilter")
const publishedFilter = defineModel<boolean | null>("publishedFilter")
const textFilter = defineModel<string>("textFilter")

const dateFilter = defineModel<Date | null>("dateFilter")

// props
withDefaults(
  defineProps<{
    showPublishedFilter?: boolean
    showTextFilter?: boolean
    textFilterLabel?: string
  }>(),
  {
    showPublishedFilter: false,
    showTextFilter: false,
    textFilterLabel: "Text",
  },
)

const { severityLevels, dataSources, reportCodes } = useValidationFilters()
</script>

<style scoped></style>
