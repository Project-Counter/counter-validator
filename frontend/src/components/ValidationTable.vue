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

    <template #loading>
      <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
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
      <v-select
        v-model="validationResultFilter"
        :items="severityLevels"
        label="Filter by validation result"
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
    </template>
  </v-data-table-server>
</template>

<script setup lang="ts">
import {
  SeverityLevel,
  severityLevelColorMap,
  severityLevelIconMap,
  Status,
  Validation,
} from "@/lib/definitions/api"
import { getValidation, getValidations, getValidationsFromUrl } from "@/lib/http/validation"
import { usePaginatedAPI } from "@/composables/paginatedAPI"
import { filesize } from "filesize"
import type { VDataTable } from "vuetify/components"
import { urls } from "@/lib/http/validation"

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
const validationResultFilter = ref<SeverityLevel[]>([])

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

// filters
const severityLevels = computed(() => [
  ...severityLevelIconMap.keys().map((k) => ({
    value: k,
    title: k,
    props: {
      "prepend-icon": "mdi-" + severityLevelIconMap.get(k),
      "append-icon": "mdi-" + severityLevelIconMap.get(k),
      "base-color": severityLevelColorMap.get(k),
    },
  })),
])

watch(validationResultFilter, () => {
  filters.validation_result = validationResultFilter.value.join(",")
  loadValidations()
})

// expose loadValidations for parent components to refresh the list
defineExpose({
  loadValidations,
})

async function start() {
  await loadValidations()
  await checkUnfinished()
}

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

onMounted(() => {
  start()
})
</script>
