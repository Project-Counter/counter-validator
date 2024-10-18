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
              <v-avatar
                class="ms-2"
                :class="'bg-' + (selectedLevels.includes(level) ? colorMap.get(level) : 'grey')"
              >
                {{ count }}
              </v-avatar>
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
import { levelColorMap as colorMap, Message, SeverityLevel } from "@/lib/definitions/api"

const p = defineProps<{
  messages: Message[]
}>()

// constants
const headers = [
  { key: "color", title: "", sortable: false },
  { key: "l", title: "Level" },
  { key: "p", title: "Position" },
  { key: "m", title: "Message" },
  { key: "h", title: "Hint" },
]

// variables
const selectedLevels = ref([...colorMap.keys()])

// computed
const filteredMessages = computed(() => {
  return p.messages.filter((m) => selectedLevels.value.includes(m.l))
})

const severityMap = computed(() => {
  const map = new Map<SeverityLevel, number>()
  p.messages.forEach((m) => {
    if (map.has(m.l)) {
      map.set(m.l, (map.get(m.l) ?? 0) + 1)
    } else {
      map.set(m.l, 1)
    }
  })
  const out = new Map<SeverityLevel, number>() // we want sorting by level from `colorMap`
  colorMap.forEach((value, k) => {
    if (map.has(k)) out.set(k, map.get(k) ?? 0)
  })
  return out
})

// methods
function toggleLevelVisibility(level: SeverityLevel) {
  if (selectedLevels.value.includes(level)) {
    selectedLevels.value = selectedLevels.value.filter((l) => l !== level)
  } else {
    selectedLevels.value = [...selectedLevels.value, level]
  }
}
</script>
