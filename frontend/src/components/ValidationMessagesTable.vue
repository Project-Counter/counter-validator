<template>
  <v-data-table
    :items="filteredMessages"
    :headers="headers"
    :items-per-page="25"
    :mobile="null"
    density="compact"
    :cell-props="({item, column}) => (column.key == 'color' ? {class: 'bg-' + colorMap.get(item.l), style: {minHeight: '4px'}} : {})"
  >
    <template #top>
      <v-row>
        <v-col
          cols="auto"
          class="align-self-center"
        >
          <v-chip
            v-for="([level, count]) in severityMap.entries()"
            :key="level"
            :color="selectedLevels.includes(level) ? colorMap.get(level) : 'grey'"
            class="ps-0 pe-1"
            size="large"
            @click="toggleLevelVisibility(level)"
          >
            <template #append>
              <v-avatar
                :class="'bg-'+(selectedLevels.includes(level) ? colorMap.get(level) : 'grey')"
                class="ms-2"
              >
                {{ count }}
              </v-avatar>
            </template>
            <template #prepend>
              <v-checkbox
                v-model="selectedLevels"
                :value="level"
                hide-details
                class="pa-0 ma-0"
                multiple
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
let selectedLevels = ref([...colorMap.keys()])

// computed
let filteredMessages = computed(() => {
  return p.messages.filter(m => selectedLevels.value.includes(m.l))
})

let severityMap = computed(() => {
  let map = new Map<SeverityLevel, number>()
  p.messages.forEach((m) => {
    if (map.has(m.l)) {
      map.set(m.l, (map.get(m.l) ?? 0) + 1)
    }
    else {
      map.set(m.l, 1)
    }
  })
  let out = new Map<SeverityLevel, number>() // we want sorting by level from `colorMap`
  colorMap.forEach((value, k) => {
    if (map.has(k)) out.set(k, map.get(k) ?? 0)
  })
  return out
})

// methods
function toggleLevelVisibility(level: SeverityLevel) {
  if (selectedLevels.value.includes(level)) {
    selectedLevels.value = selectedLevels.value.filter(l => l !== level)
  }
  else {
    selectedLevels.value = [...selectedLevels.value, level]
  }
}
</script>
