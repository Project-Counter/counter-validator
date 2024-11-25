<template>
  <v-table density="compact">
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
</template>

<script setup lang="ts">
import { getValidationMessageStats } from "@/lib/http/message"
import { SeverityLevel, severityLevelColorMap, Validation } from "@/lib/definitions/api"
import { formatInteger, formatPercent } from "../lib/formatting"

const props = defineProps<{
  validation: Validation
}>()

// messages stats
const stats = ref<{ summary: string; severity: SeverityLevel; count: number }[]>([])
const total = ref(0)
async function getMessagesStats() {
  stats.value = (await getValidationMessageStats(props.validation.id)).summary_severity
  total.value = stats.value.reduce((acc, curr) => acc + curr.count, 0)
}

// on mount
onMounted(getMessagesStats)
</script>
