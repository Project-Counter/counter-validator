<template>
  <table>
    <tbody>
      <tr
        v-for="(value, level) in stats"
        :key="level"
      >
        <td class="me-3 text-caption text-right">{{ value }}</td>

        <td>
          <v-icon
            :color="severityLevelColorMap.get(level)"
            size="16"
            >mdi-circle
          </v-icon>
        </td>
        <td>{{ level }}</td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
import { SeverityLevel, severityLevelColorMap } from "@/lib/definitions/api"

defineProps<{ stats: Record<SeverityLevel, number> }>()
</script>
