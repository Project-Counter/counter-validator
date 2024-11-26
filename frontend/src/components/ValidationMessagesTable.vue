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
        <v-col>
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
                hide-details
                multiple
                :value="level"
              />
            </template>

            {{ level }}
          </v-chip>
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
  }
}

watch([selectedLevels], () => {
  filters.severity = selectedLevels.value.join(",")
  getMessages()
})
</script>
