<template>
  <v-data-table-server
    v-model:items-per-page="params.pageSize"
    v-model:page="params.page"
    v-model:sort-by="params.sortBy"
    :headers="headers"
    :items="items"
    density="compact"
    :items-length="totalCount"
    :loading="loading"
    @update:options="load"
  >
    <template #item.created="{ item }">
      <IsoDateTime :date-string="item.created" />
    </template>

    <template #item.status="{ item }">
      <validation-status :validation="item" />
    </template>

    <template #item.validation_result="{ item }">
      <SeverityLevelChip :severity="item.validation_result" />
    </template>

    <template #item.file_size="{ item }">
      {{ filesize(item.file_size) }}
    </template>

    <template #item.used_memory="{ item }">
      {{ filesize(item.used_memory) }}
    </template>

    <template #item.duration="{ item }"> {{ Math.round(1000 * item.duration) }} ms </template>

    <template #item.stats="{ item }">
      <StatsPie :item="item" />
    </template>

    <template #top>
      <ValidationFilterSet
        v-model:validation-result-filter="validationResultFilter"
        v-model:cop-version-filter="copVersionFilter"
        v-model:report-code-filter="reportCodeFilter"
        v-model:endpoint-filter="endpointFilter"
        v-model:source-filter="sourceFilter"
      />
    </template>
  </v-data-table-server>
</template>

<script setup lang="ts">
import { ValidationCore } from "@/lib/definitions/api"
import { getValidationCoresFromUrl, urls } from "@/lib/http/validation"
import { filesize } from "filesize"
import type { VDataTable } from "vuetify/components"
import { usePaginatedAPI } from "@/composables/paginatedAPI"
import { useValidationFilters } from "@/composables/validationFiltering"

const items = ref<ValidationCore[]>([])

type ReadonlyHeaders = VDataTable["$props"]["headers"]

const headers: ReadonlyHeaders = [
  { key: "created", title: "Time" },
  { key: "status", title: "Status", width: 1 },
  { key: "cop_version", title: "COP version" },
  { key: "report_code", title: "Report id" },
  { key: "validation_result", title: "Validation Result" },
  { key: "file_size", title: "File size", align: "end" },
  { key: "used_memory", title: "Used memory", align: "end" },
  { key: "duration", title: "Duration", align: "end" },
  { key: "stats", title: "Stats", align: "end" },
]

const { url, params, filters } = usePaginatedAPI(urls.coreList)
const loading = ref(false)
const totalCount = ref(0)

const { validationResultFilter, copVersionFilter, reportCodeFilter, endpointFilter, sourceFilter } =
  useValidationFilters()

watchEffect(() => {
  filters.validation_result = validationResultFilter.value.join(",")
  filters.cop_version = copVersionFilter.value.join(",")
  filters.report_code = reportCodeFilter.value.join(",")
  filters.api_endpoint = endpointFilter.value.join(",")
  filters.data_source = sourceFilter.value.join(",")
  load()
})

// loading of data
async function load() {
  loading.value = true
  try {
    const { count, results } = await getValidationCoresFromUrl(url.value)
    items.value = results
    totalCount.value = count
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
})
</script>
