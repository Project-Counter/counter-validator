<template>
  <v-data-table
    :headers="headers"
    :items="items"
    density="compact"
  >
    <template #item.created="{ item }">
      <IsoDateTime :date-string="item.created" />
    </template>

    <template #item.status="{ item }">
      <validation-status :validation="item" />
    </template>

    <template #item.validation_result="{ item }">
      <ValidationResult :item="item" />
    </template>

    <template #item.file_size="{ item }">
      {{ filesize(item.file_size) }}
    </template>

    <template #item.used_memory="{ item }">
      {{ filesize(item.used_memory) }}
    </template>

    <template #item.duration="{ item }"> {{ Math.round(1000 * item.duration) }} ms </template>

    <template #item.platform_name="{ item }">
      <span v-if="item.platform">
        <a
          :href="'https://registry.countermetrics.org/platform/' + item.platform"
          target="_blank"
          >{{ item.platform_name }}
        </a>
        <v-icon
          size="x-small"
          class="ps-1"
          >mdi-open-in-new</v-icon
        >
      </span>
      <span v-else>{{ item.platform_name }}</span>
    </template>

    <template #item.stats="{ item }">
      <StatsPie :item="item" />
      <!--      <StatsChip :item="item" />-->
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import { ValidationCore } from "@/lib/definitions/api"
import { getValidationCores } from "@/lib/http/validation"
import ValidationResult from "@/components/ValidationResultChip.vue"
import { filesize } from "filesize"
import type { VDataTable } from "vuetify/components"
import StatsPie from "@/components/StatsPie.vue"

const items = ref<ValidationCore[]>([])

type ReadonlyHeaders = VDataTable["$props"]["headers"]

const headers: ReadonlyHeaders = [
  { key: "created", title: "Time" },
  { key: "status", title: "Status", width: 1 },
  { key: "cop_version", title: "COP version" },
  { key: "report_code", title: "Report code" },
  { key: "platform_name", title: "Platform" },
  { key: "validation_result", title: "Validation Result" },
  { key: "file_size", title: "File size", align: "end" },
  { key: "used_memory", title: "Used memory", align: "end" },
  { key: "duration", title: "Duration", align: "end" },
  { key: "stats", title: "Stats", align: "end" },
]

async function load() {
  items.value = await getValidationCores()
}
load().then()
</script>
