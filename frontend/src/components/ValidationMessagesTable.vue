<template>
  <v-data-table
    :cell-props="
      ({ item, column }) =>
        column.key == 'color'
          ? { class: 'bg-' + colorMap.get(item.severity), style: { minHeight: '4px' } }
          : {}
    "
    density="compact"
    :headers="headers"
    :items="filteredMessages"
    :items-per-page="25"
    :mobile="null"
  >
    <template #top>
      <v-row>
        <v-col
          class="align-self-center"
          cols="auto"
        >
          <v-chip
            v-for="[level, count] in severityMap.entries()"
            :key="level"
            class="ps-0 pe-1"
            :color="selectedLevels.includes(level) ? colorMap.get(level) : 'grey'"
            size="large"
            @click="toggleLevelVisibility(level)"
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
      <v-row>
        <v-col cols="auto">
          <v-table density="compact">
            <tbody>
              <tr
                v-for="stat in stats"
                :key="`${stats.severity}-${stat.summary}`"
              >
                <td>
                  <SeverityLevelChip
                    :severity="stat.severity"
                    variant="text"
                  />
                </td>
                <td>{{ stat.summary }}</td>
                <td class="text-right">{{ formatInteger(stat.count) }}</td>
                <td class="text-right">{{ formatPercent(stat.count / total) }}</td>
                <td>
                  <span
                    :style="{
                      width: `${Math.round((100 * stat.count) / total)}px`,
                    }"
                    class="d-inline-block"
                    :class="`bg-${severityLevelColorMap.get(stat.severity)}`"
                    >&nbsp;</span
                  >
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-col>
      </v-row>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import {
  severityLevelColorMap as colorMap,
  Message,
  SeverityLevel,
  Validation,
  severityLevelColorMap,
} from "@/lib/definitions/api"
import { getValidationMessages, getValidationMessageStats } from "@/lib/http/message"
import SeverityLevelChip from "@/components/SeverityLevelChip.vue"
import { formatInteger, formatPercent } from "../lib/formatting"

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
async function getMessages() {
  messages.value = await getValidationMessages(props.validation.id)
}

const filteredMessages = computed(() => {
  return messages.value.filter((m) => selectedLevels.value.includes(m.severity))
})

// messages stats
const stats = ref<{ summary: string; severity: number; count: number }[]>([])
const total = ref(0)
async function getMessagesStats() {
  stats.value = (await getValidationMessageStats(props.validation.id)).summary_severity
  total.value = stats.value.reduce((acc, curr) => acc + curr.count, 0)
  console.log(stats.value)
}

// on mount
onMounted(getMessages)
onMounted(getMessagesStats)
</script>
