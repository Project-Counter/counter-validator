<template>
  <v-data-table-server
    v-model="selected"
    v-model:items-per-page="params.pageSize"
    v-model:page="params.page"
    v-model:sort-by="params.sortBy"
    :headers="headers"
    :items="items"
    :mobile="null"
    no-data-text="No validations in your history"
    :loading="loading"
    color="primary"
    :show-select="props.selectable"
    item-value="id"
    :items-length="totalCount"
    @update:options="loadValidations"
  >
    <template #item.status="{ item }">
      <router-link
        v-if="item.id && item.status === Status.SUCCESS"
        :to="`validation/${item.id}/`"
      >
        <ValidationStatus :validation="item" />
      </router-link>
      <ValidationStatus
        v-else
        :validation="item"
      />
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

    <template #item.created="{ item }">
      <DateTooltip :date="item.created" />
    </template>

    <template #item.expiration_date="{ item }">
      <DateTooltip
        v-if="item.expiration_date"
        :date="item.expiration_date"
      />
      <span v-else>-</span>
    </template>

    <template #item.filename="{ item }">
      <router-link :to="'validation/' + item.id + '/'">
        {{ item.filename || "Unknown" }}
      </router-link>
    </template>

    <template #item.file_size="{ item }">
      {{ filesize(item.file_size) }}
    </template>

    <template #item.api_key_prefix="{ item }">
      <v-tooltip>
        <template #activator="{ props }">
          <v-icon
            v-bind="props"
            color="disabled"
            >{{ item.api_key_prefix === "" ? "mdi-account" : "mdi-api" }}
          </v-icon>
        </template>
        {{ item.api_key_prefix === "" ? "Manual" : "API" }}
      </v-tooltip>
    </template>

    <template #item.data_source="{ item }">
      <v-tooltip>
        <template #activator="{ props }">
          <v-icon
            v-bind="props"
            color="disabled"
            >{{ item.data_source === "file" ? "mdi-file-outline" : "mdi-cloud-outline" }}
          </v-icon>
        </template>
        <span>{{ item.data_source === "file" ? "File" : "COUNTER API" }}</span>
      </v-tooltip>
    </template>

    <template #top>
      <v-row>
        <v-col>
          <v-select
            v-model="sourceFilter"
            :items="dataSources"
            label="Data source"
            multiple
            clearable
          />
        </v-col>

        <v-col>
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

        <v-col>
          <v-select
            v-model="copVersionFilter"
            :items="copVersions"
            label="CoP version"
            multiple
            clearable
          />
        </v-col>

        <v-col>
          <v-select
            v-model="endpointFilter"
            :items="counterAPIEndpoints"
            label="Endpoint"
            multiple
            clearable
          />
        </v-col>

        <v-col>
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
  </v-data-table-server>
</template>

<script setup lang="ts">
import {
  severityLevelColorMap,
  severityLevelIconMap,
  Status,
  Validation,
} from "@/lib/definitions/api"
import { getValidation, getValidationsFromUrl, urls } from "@/lib/http/validation"
import { usePaginatedAPI } from "@/composables/paginatedAPI"
import { filesize } from "filesize"
import type { VDataTable } from "vuetify/components"
import { useValidationFilters } from "@/composables/validationFiltering"

const props = withDefaults(
  defineProps<{
    selectable?: boolean
  }>(),
  {
    selectable: false,
  },
)

const selected = defineModel<string[]>("selected")

const items = ref<Validation[]>([])
let loading = ref(false)

type ReadonlyHeaders = VDataTable["$props"]["headers"]

const headers: ReadonlyHeaders = [
  { key: "status", title: "Status", width: 1 },
  { key: "data_source", title: "Data source", sortable: false },
  { key: "api_key_prefix", title: "Submission method", sortable: false },
  { key: "filename", title: "Filename" },
  { key: "file_size", title: "File size", align: "end" },
  { key: "platform_name", title: "Platform" },
  { key: "cop_version", title: "COP version" },
  { key: "report_code", title: "Report code" },
  { key: "validation_result", title: "Validation result" },
  { key: "created", title: "Created" },
  { key: "expiration_date", title: "Expiration" },
]

// validations list
const { url, params, filters } = usePaginatedAPI(urls.list)
const totalCount = ref(0)

const {
  validationResultFilter,
  copVersionFilter,
  reportCodeFilter,
  endpointFilter,
  sourceFilter,
  severityLevels,
  dataSources,
  reportCodes,
  copVersions,
  counterAPIEndpoints,
} = useValidationFilters()

watchEffect(() => {
  filters.validation_result = validationResultFilter.value.join(",")
  filters.cop_version = copVersionFilter.value.join(",")
  filters.report_code = reportCodeFilter.value.join(",")
  filters.api_endpoint = endpointFilter.value.join(",")
  filters.data_source = sourceFilter.value.join(",")
  loadValidations()
})

async function loadValidations() {
  loading.value = true
  try {
    const { count, results } = await getValidationsFromUrl(url.value)
    items.value = results
    totalCount.value = count
  } finally {
    loading.value = false
  }
}

// expose loadValidations for parent components to refresh the list
defineExpose({
  loadValidations,
})

// check for unfinished validations and periodically update the list

async function checkUnfinished() {
  let unfinished = items.value.filter(
    (v) => v.status === Status.RUNNING || v.status === Status.WAITING,
  )
  let fetchers = unfinished.map((v) => getValidation(v.id))
  for (let result of await Promise.all(fetchers)) {
    let index = items.value.findIndex((v) => v.id === result.id)
    items.value[index] = result
  }
  unfinished = items.value.filter((v) => v.status === Status.RUNNING || v.status === Status.WAITING)
  if (unfinished.length > 0) {
    setTimeout(checkUnfinished, 1000)
  }
}

// start

async function start() {
  await loadValidations()
  await checkUnfinished()
}

onMounted(() => {
  start()
})
</script>
