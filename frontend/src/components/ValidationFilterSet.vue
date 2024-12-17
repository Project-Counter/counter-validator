<template>
  <v-row>
    <v-col
      v-if="showPublishedFilter"
      cols="12"
      sm="4"
      md="3"
      lg="2"
      xl="1"
    >
      <v-select
        v-model="publishedFilter"
        :items="booleanOptions"
        label="Shared"
        hide-details
      />
    </v-col>

    <v-col
      cols="12"
      sm="8"
      md="4"
      lg="3"
      xl="2"
    >
      <v-select
        v-model="sourceFilter"
        :items="dataSources"
        label="Data source"
        multiple
        clearable
        hide-details
      />
    </v-col>

    <v-col
      cols="12"
      sm="8"
      md="5"
      lg="4"
      xl="3"
      xxl="2"
    >
      <v-select
        v-model="validationResultFilter"
        :items="severityLevels"
        label="Validation result"
        multiple
        clearable
        hide-details
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
      sm="4"
      md="3"
      lg="2"
      xl="2"
      xxl="1"
    >
      <v-select
        v-model="copVersionFilter"
        :items="copVersions"
        label="CoP version"
        multiple
        clearable
        hide-details
      />
    </v-col>

    <v-col
      cols="12"
      sm="6"
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
        hide-details
      />
    </v-col>

    <v-col
      cols="12"
      sm="6"
      md="3"
      lg="3"
      xl="2"
      xxl="1"
    >
      <v-select
        v-model="reportCodeFilter"
        :items="reportCodes"
        label="Report ID"
        multiple
        clearable
        hide-details
      />
    </v-col>

    <v-col
      v-if="showTextFilter"
      cols="12"
      sm="6"
      md="4"
      lg="3"
      xl="2"
    >
      <v-text-field
        v-model="textFilter"
        label="User note"
        hide-details
        clearable
        append-inner-icon="mdi-magnify"
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

const validationResultFilter = defineModel<SeverityLevel[]>("validationResultFilter")
const copVersionFilter = defineModel<CoP[]>("copVersionFilter")
const reportCodeFilter = defineModel<ReportCode[]>("reportCodeFilter")
const endpointFilter = defineModel<CounterAPIEndpoint[]>("endpointFilter")
const sourceFilter = defineModel<DataSource[]>("sourceFilter")
const publishedFilter = defineModel<boolean | null | undefined>("publishedFilter")
const showPublishedFilter = defineModel<boolean>("showPublishedFilter")
const textFilter = defineModel<string>("textFilter")
const showTextFilter = defineModel<boolean>("showTextFilter")

const { severityLevels, dataSources, reportCodes } = useValidationFilters()
</script>

<style scoped></style>
