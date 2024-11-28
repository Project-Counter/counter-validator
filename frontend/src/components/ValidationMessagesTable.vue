<template>
  <v-data-table-server
    v-model:items-per-page="params.pageSize"
    v-model:page="params.page"
    v-model:sort-by="params.sortBy"
    :cell-props="
      ({ item, column }) =>
        column.key == 'color'
          ? { class: 'bg-' + colorMap.get(item.severity), style: { minHeight: '4px' } }
          : {}
    "
    density="compact"
    :headers="headers"
    :items="messages"
    :mobile="null"
    :items-length="totalCount"
    @update:options="getMessages"
  >
    <template #top>
      <v-row class="pb-6">
        <v-col class="mt-3">
          <v-chip
            v-for="[level, count] in severityMap.entries()"
            :key="level"
            class="ps-0 pe-1"
            :color="selectedLevels.includes(level) ? colorMap.get(level) : 'grey'"
            size="large"
            @click.stop="toggleLevelVisibility(level)"
          >
            <template #append>
              <v-chip
                class="ms-2 text-caption"
                :class="'bg-' + (selectedLevels.includes(level) ? colorMap.get(level) : 'grey')"
                variant="text"
              >
                {{ count }}
              </v-chip>
            </template>
            <template #prepend>
              <v-checkbox
                v-model="selectedLevels"
                class="pa-0 ma-0"
                :hide-details="true"
                multiple
                :value="level"
              />
            </template>

            {{ level }}
          </v-chip>
        </v-col>
        <v-col>
          <v-text-field
            v-model="search"
            label="Search"
            clearable
            dense
          ></v-text-field>
        </v-col>
      </v-row>
    </template>
  </v-data-table-server>
</template>

<script setup lang="ts">
import {
  Message,
  SeverityLevel,
  severityLevelColorMap as colorMap,
  Validation,
} from "@/lib/definitions/api"
import { getValidationMessagesFromUrl } from "@/lib/http/message"
import { usePaginatedAPI } from "@/composables/paginatedAPI"
import { urls } from "@/lib/http/validation"
import { HttpStatusError } from "@/lib/http/util"
import debounce from "lodash/debounce"

const props = defineProps<{
  validation: Validation
}>()

const messages = ref<Message[]>([])

// constants
const headers = [
  { key: "color", title: "", sortable: false },
  { key: "severity", title: "Severity" },
  { key: "location", title: "Location" },
  { key: "data", title: "Data" },
  { key: "message", title: "Message" },
  // { key: "summary", title: "Summary" },
  { key: "hint", title: "Hint" },
]

// level visibility
const selectedLevels = ref([...colorMap.keys()])

function toggleLevelVisibility(level: SeverityLevel) {
  if (selectedLevels.value.includes(level)) {
    selectedLevels.value = selectedLevels.value.filter((l) => l !== level)
  } else {
    selectedLevels.value = [...selectedLevels.value, level]
  }
}

const severityMap = computed(() => {
  const out = new Map<SeverityLevel, number>() // we want sorting by level from `colorMap`
  colorMap.forEach((value, k) => {
    if (props.validation.stats[k]) out.set(k, props.validation.stats[k])
  })
  return out
})

// messages
const { url, params, filters } = usePaginatedAPI(`${urls.list}${props.validation.id}/messages/`)
const totalCount = ref(0)

async function getMessages() {
  try {
    const { results: m, count } = await getValidationMessagesFromUrl(url.value)
    messages.value = m
    totalCount.value = count
  } catch (err) {
    if (err instanceof HttpStatusError && err?.res?.status === 404) {
      if (params.page > 1) {
        params.page = 1
        getMessages()
        return
      }
      messages.value = []
      totalCount.value = 0
      return
    }
    throw err
  }
}

// filter
function applyFilterByMessage(message: Message) {
  selectedLevels.value = [message.severity]
  search.value = message.summary
}
defineExpose({ applyFilterByMessage })

// search
const search = ref("")

watch(selectedLevels, () => {
  filters.severity = selectedLevels.value.join(",")
  getMessages()
})

watch(
  search,
  debounce(() => {
    filters.search = search.value || ""
    getMessages()
  }, 300),
)
</script>
