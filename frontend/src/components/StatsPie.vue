<template>
  <span>
    <v-tooltip v-if="Object.keys(p.item.stats).length > 0">
      <template #activator="{ props }">
        <span v-bind="props">
          <SimplePie :parts="statParts" />
        </span>
      </template>
      <table>
        <tbody>
          <tr
            v-for="(value, level) in p.item.stats"
            :key="level"
          >
            <td class="me-3 text-caption text-right">{{ value }}</td>

            <td>
              <v-icon
                :color="severityLevelColorMap.get(level)"
                size="16"
                >mdi-circle</v-icon
              >
            </td>
            <td>{{ level }}</td>
          </tr>
        </tbody>
      </table>
    </v-tooltip>
  </span>
</template>

<script setup lang="ts">
import { defineProps } from "vue"
import { ValidationBase, severityLevelColorMap } from "@/lib/definitions/api"
import SimplePie from "@/components/SimplePie.vue"
import { useTheme } from "vuetify"
import type { Entries } from "type-fest"

const vTheme = useTheme()

let p = defineProps<{
  item: ValidationBase
}>()

const statParts = computed(() =>
  (Object.entries(p.item.stats) as Entries<typeof p.item.stats>).map(([level, value]) => ({
    size: value,
    color: vTheme.current.value.colors[severityLevelColorMap.get(level) ?? "grey"],
  })),
)
</script>

<style scoped></style>
