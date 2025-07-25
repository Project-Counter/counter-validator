<template>
  <v-data-table-server
    v-model:items-per-page="pageSize"
    v-model:page="page"
    v-model:sort-by="sortBy"
    :headers="headers"
    :items="items"
    density="compact"
    :items-length="totalCount"
    :loading="loading"
  >
    <template #item.created="{ item }">
      <IsoDateTime :date-string="item.created" />
    </template>

    <template #item.status="{ item }">
      <validation-status :validation="item" />
    </template>

    <template #item.validation_result="{ item }">
      <v-tooltip>
        <template #activator="{ props }">
          <SeverityLevelChip
            :severity="item.validation_result"
            v-bind="props"
          />
        </template>
        <StatsTableSimple :stats="item.stats" />
      </v-tooltip>
    </template>

    <template #item.file_size="{ item }">
      {{ filesize(item.file_size) }}
    </template>

    <template #item.used_memory="{ item }">
      {{ filesize(item.used_memory) }}
    </template>

    <template #item.duration="{ item }"> {{ Math.round(1000 * item.duration) }} ms </template>

    <template #item.user="{ item }">
      <UserName
        class="text-caption"
        :user="item.user"
      />
    </template>

    <template #top>
      <ValidationFilterSet
        v-model:validation-result-filter="validationResultFilter"
        v-model:cop-version-filter="copVersionFilter"
        v-model:report-code-filter="reportCodeFilter"
        v-model:endpoint-filter="endpointFilter"
        v-model:source-filter="sourceFilter"
        v-model:text-filter="textFilter"
        v-model:date-filter="dateFilter"
        text-filter-label="User"
        show-text-filter
        class="pb-8"
      />
    </template>
  </v-data-table-server>
</template>

<script setup lang="ts">
import { ValidationCore, Status } from "@/lib/definitions/api"
import { getValidationCoresFromUrl, urls, getValidationCoreDetail } from "@/lib/http/validation"
import { filesize } from "filesize"
import type { VDataTable } from "vuetify/components"
import { usePaginatedAPI } from "@/composables/paginatedAPI"
import { useValidationFilters } from "@/composables/validationFiltering"
import { usePaginationWithMemory } from "@/composables/usePaginationWithMemory"
import { HttpStatusError } from "@/lib/http/util"
import { useDate } from "vuetify"

const items = ref<ValidationCore[]>([])

type ReadonlyHeaders = VDataTable["$props"]["headers"]

const headers: ReadonlyHeaders = [
  { key: "created", title: "Time" },
  { key: "user", title: "User" },
  { key: "status", title: "Status", width: 1 },
  { key: "cop_version", title: "COP version" },
  { key: "report_code", title: "Report id" },
  { key: "validation_result", title: "Validation Result" },
  { key: "file_size", title: "File size", align: "end" },
  { key: "used_memory", title: "Used memory", align: "end" },
  { key: "duration", title: "Duration", align: "end" },
]

const { url, params, filters } = usePaginatedAPI(urls.coreList)
const loading = ref(false)
const totalCount = ref(0)
const { page, pageSize, sortBy } = usePaginationWithMemory(params)

const {
  validationResultFilter,
  copVersionFilter,
  reportCodeFilter,
  endpointFilter,
  sourceFilter,
  textFilter,
  dateFilter,
} = useValidationFilters()

const dateAdapter = useDate()

// the effect will also load data in the beginning
watch(
  () =>
    [
      url.value,
      validationResultFilter.value.join(","),
      copVersionFilter.value.join(","),
      reportCodeFilter.value.join(","),
      endpointFilter.value.join(","),
      sourceFilter.value.join(","),
      textFilter.value,
      dateFilter.value,
    ].join("---"),
  () => {
    filters.validation_result = validationResultFilter.value.join(",")
    filters.cop_version = copVersionFilter.value.join(",")
    filters.report_code = reportCodeFilter.value.join(",")
    filters.api_endpoint = endpointFilter.value.join(",")
    filters.data_source = sourceFilter.value.join(",")
    filters.search = textFilter.value
    if (dateFilter.value) {
      filters.date = dateAdapter.toISO(dateFilter.value)
      filters.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
    } else delete filters.date
    load()
  },
  { immediate: true },
)

let lastUrl = ref("")
// loading of data
async function load() {
  if (url.value === lastUrl.value) return
  lastUrl.value = url.value
  loading.value = true
  try {
    const { count, results } = await getValidationCoresFromUrl(url.value)
    items.value = results
    totalCount.value = count
  } catch (e) {
    if (e instanceof HttpStatusError && e.res?.status === 404 && page.value > 1) {
      console.log("404, resetting page to 1")
      page.value = 1
    } else {
      throw e
    }
  } finally {
    loading.value = false
    await checkUnfinished()
  }
}

// check for unfinished validations and periodically update the list
let checkTimeout: number | null = null

async function checkUnfinished() {
  let unfinished = items.value.filter(
    (v) => v.status === Status.RUNNING || v.status === Status.WAITING,
  )
  let fetchers = unfinished.map((v) => getValidationCoreDetail(v.id))
  for (let result of await Promise.all(fetchers)) {
    let index = items.value.findIndex((v) => v.id === result.id)
    items.value[index] = result
  }
  unfinished = items.value.filter((v) => v.status === Status.RUNNING || v.status === Status.WAITING)
  if (unfinished.length > 0) {
    checkTimeout = setTimeout(checkUnfinished, 1000)
  } else {
    checkTimeout = null
  }
}

onUnmounted(() => {
  if (checkTimeout) clearTimeout(checkTimeout)
})
</script>
