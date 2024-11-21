<template>
  <v-data-table
    :cell-props="
      ({ item, column }) =>
        column.key == 'color'
          ? { class: 'bg-' + colorMap.get(item.l), style: { minHeight: '4px' } }
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
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import {
  levelColorMap as colorMap,
  Message,
  SeverityLevel,
  Validation,
} from "@/lib/definitions/api"
import { getValidationMessages } from "@/lib/http/message"

const props = defineProps<{
  validation: Validation
}>()

const messages = ref<Message[]>([])

// constants
const headers = [
  { key: "color", title: "", sortable: false },
  { key: "severity", title: "Severity" },
  { key: "location", title: "Location" },
  { key: "message", title: "Message" },
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

// on mount
onMounted(getMessages)
</script>
