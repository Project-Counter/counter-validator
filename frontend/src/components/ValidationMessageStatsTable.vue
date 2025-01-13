<template>
  <v-table density="compact">
    <thead>
      <tr>
        <th>Severity</th>
        <th>Summary</th>
        <th class="text-right">Count</th>
        <th class="text-right">Percentage</th>
        <th>Graph</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="stat in stats"
        :key="`${stat.severity}-${stat.summary}`"
      >
        <td>
          <SeverityLevelChip
            :severity="stat.severity"
            variant="text"
          />
        </td>
        <td>
          {{ stat.summary }}
        </td>
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
        <td>
          <v-btn
            size="x-small"
            variant="text"
            @click="emit('select-message', stat)"
          >
            <v-icon class="mr-1">mdi-filter-outline</v-icon>
            Apply filter
          </v-btn>
        </td>
      </tr>
    </tbody>
  </v-table>
</template>

<script setup lang="ts">
import { getValidationMessageStats } from "@/lib/http/message"
import { SeverityLevel, severityLevelColorMap, Validation } from "@/lib/definitions/api"
import { formatInteger, formatPercent } from "../lib/formatting"

const props = withDefaults(
  defineProps<{
    validation: Validation
    publicView?: boolean
  }>(),
  {
    publicView: false,
  },
)

const emit = defineEmits(["select-message"])

// messages stats
const stats = ref<{ summary: string; severity: SeverityLevel; count: number }[]>([])
const total = ref(0)
async function getMessagesStats() {
  const usedId = props.publicView ? props.validation.public_id || "" : props.validation.id
  stats.value = (await getValidationMessageStats(usedId)).summary_severity
  total.value = stats.value.reduce((acc, curr) => acc + curr.count, 0)
}

// on mount
onMounted(getMessagesStats)
</script>
