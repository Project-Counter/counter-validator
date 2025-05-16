<template>
  <v-data-table-server
    v-model="selected"
    v-model:items-per-page="pageSize"
    v-model:page="page"
    v-model:sort-by="sortBy"
    :headers="headers"
    :items="items"
    :mobile="null"
    no-data-text="No validations in your history"
    :loading="loading"
    color="primary"
    :show-select="props.selectable"
    item-value="id"
    :items-length="totalCount"
  >
    <template #item.status="{ item }">
      <router-link
        v-if="item.id && item.status === Status.SUCCESS"
        :to="`/validation/${item.id}/`"
      >
        <ValidationStatus :validation="item" />
      </router-link>
      <ValidationStatus
        v-else
        :validation="item"
      />

      <v-tooltip
        bottom
        max-width="600px"
      >
        <template #activator="{ props }">
          <v-icon
            v-if="item.public_id"
            v-bind="props"
            color="subdued"
            >mdi-eye</v-icon
          >
        </template>
        This validation was made publicly visible using a unique link.
      </v-tooltip>
    </template>

    <template #item.validation_result="{ item }">
      <v-tooltip v-if="item.stats && Object.keys(item.stats).length > 0">
        <template #activator="{ props }">
          <SeverityLevelChip
            :severity="item.validation_result"
            v-bind="props"
          />
        </template>
        <StatsTableSimple :stats="item.stats" />
      </v-tooltip>
      <!-- no tooltip if there are no stats -->
      <SeverityLevelChip
        v-else
        :severity="item.validation_result"
      />
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
      <router-link :to="'/validation/' + item.id + '/'">
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

    <template #item.user_note="{ item }">
      <ShortenText
        v-if="item.user_note"
        :text="item.user_note"
        :length="20"
      />
    </template>

    <template #item.user="{ item }">
      <UserName
        :user="item.user"
        class="text-caption"
      />
    </template>

    <template #top>
      <ValidationFilterSet
        v-model:validation-result-filter="validationResultFilter"
        v-model:cop-version-filter="copVersionFilter"
        v-model:report-code-filter="reportCodeFilter"
        v-model:endpoint-filter="endpointFilter"
        v-model:source-filter="sourceFilter"
        v-model:published-filter="publishedFilter"
        v-model:text-filter="textFilter"
        show-published-filter
        show-text-filter
        :text-filter-label="admin ? 'Note, filename, user' : 'Note, filename'"
        class="pb-8"
      />
    </template>
  </v-data-table-server>
</template>

<script setup lang="ts">
import { Status, Validation } from "@/lib/definitions/api"
import { getValidationDetail, getValidationsFromUrl, urls } from "@/lib/http/validation"
import { usePaginatedAPI } from "@/composables/paginatedAPI"
import { filesize } from "filesize"
import { useValidationFilters } from "@/composables/validationFiltering"
import debounce from "lodash/debounce"
import { DataTableHeader } from "@/lib/vuetifyTypes"
import UserName from "@/components/UserName.vue"
import ShortenText from "@/components/ShortenText.vue"
import { usePaginationWithMemory } from "@/composables/usePaginationWithMemory"
import { HttpStatusError } from "@/lib/http/util"

const props = withDefaults(
  defineProps<{
    selectable?: boolean
    admin?: boolean
  }>(),
  {
    selectable: false,
    admin: false,
  },
)

const selected = defineModel<string[]>("selected")

const items = ref<Validation[]>([])
let loading = ref(false)

let headers: DataTableHeader[] = [
  { key: "status", title: "Status", width: 1 },
  { key: "data_source", title: "Data source", sortable: false },
  { key: "api_key_prefix", title: "Submission method", sortable: false },
  { key: "filename", title: "Filename" },
  { key: "file_size", title: "File size", align: "end" },
  { key: "user_note", title: "Note" },
  { key: "cop_version", title: "COP version" },
  { key: "report_code", title: "Report id" },
  { key: "validation_result", title: "Validation result" },
  { key: "created", title: "Created" },
  { key: "expiration_date", title: "Expiration" },
]

if (props.admin) {
  headers.splice(2, 0, { key: "user", title: "User", sortable: false })
}

// validations list
const { url, params, filters } = usePaginatedAPI(props.admin ? urls.adminList : urls.list)
const { page, pageSize, sortBy } = usePaginationWithMemory(params)
const totalCount = ref(0)
const lastUrl = ref("")

const {
  validationResultFilter,
  copVersionFilter,
  reportCodeFilter,
  endpointFilter,
  sourceFilter,
  publishedFilter,
  textFilter,
} = useValidationFilters()

function updateNormalFilters() {
  filters.validation_result = validationResultFilter.value.join(",")
  filters.cop_version = copVersionFilter.value.join(",")
  filters.report_code = reportCodeFilter.value.join(",")
  filters.api_endpoint = endpointFilter.value.join(",")
  filters.data_source = sourceFilter.value.join(",")
  if (publishedFilter.value != null) filters.published = publishedFilter.value.toString()
  else delete filters.published
}

// note: we need to watch a combined value of all filters because using useRouteQuery
//       in useValidationFilters means new arrays are created on each change, which causes
//       the watcher to trigger even if the values are the same
watch(
  () =>
    [
      url.value,
      publishedFilter.value ? publishedFilter.value.toString() : "",
      copVersionFilter.value.join(","),
      reportCodeFilter.value.join(","),
      validationResultFilter.value.join(","),
      endpointFilter.value.join(","),
      sourceFilter.value.join(","),
    ].join("---"),
  () => {
    updateNormalFilters()
    loadValidations()
  },
)

function updateDebouncedFilters() {
  filters.search = textFilter.value || ""
}

watch(
  textFilter,
  debounce(() => {
    console.debug("textFilter changed", textFilter.value)
    updateDebouncedFilters()
    loadValidations()
  }, 300),
)

async function loadValidations(force = false) {
  if (url.value === lastUrl.value && !force) return
  lastUrl.value = url.value
  loading.value = true
  try {
    const { count, results } = await getValidationsFromUrl(url.value)
    items.value = results
    totalCount.value = count
  } catch (e) {
    // if there is 404 and the page is set to > 1, we want to reset the page
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

// expose loadValidations for parent components to refresh the list
defineExpose({
  loadValidations,
})

// check for unfinished validations and periodically update the list
let checkTimeout: number | null = null

async function checkUnfinished() {
  let unfinished = items.value.filter(
    (v) => v.status === Status.RUNNING || v.status === Status.WAITING,
  )
  let fetchers = unfinished.map((v) => getValidationDetail(v.id))
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

onMounted(() => {
  updateNormalFilters()
  updateDebouncedFilters()
  loadValidations()
})

onUnmounted(() => {
  console.log("Cleaning up ValidationTable on unmount")
  if (checkTimeout) clearTimeout(checkTimeout)
})
</script>
