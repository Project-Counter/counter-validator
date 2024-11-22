<template>
  <v-data-table
    :headers="headers"
    :items="items"
    :mobile="null"
    no-data-text="No validations in your history"
    :loading="loading"
    color="primary"
  >
    <template #item.status="{ item }">
      <validation-status :validation="item" />
    </template>

    <template #item.validation_result="{ item }">
      <SeverityLevelChip :severity="item.validation_result" />
    </template>

    <template #item.created="{ item }">
      <date-tooltip :date="item.created" />
    </template>

    <template #item.filename="{ item }">
      <router-link :to="'validation/' + item.id + '/'">
        {{ item.filename || "Unknown" }}
      </router-link>
    </template>

    <template #item.file_size="{ item }">
      {{ filesize(item.file_size) }}
    </template>

    <template #item.api_key_prefix="{ item }">
      <v-icon color="disabled">{{ item.api_key_prefix === "" ? "mdi-account" : "mdi-api" }}</v-icon>
    </template>

    <template #item.stats="{ item }">
      <StatsPie :item="item" />
    </template>

    <template #loading>
      <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
    </template>

    <template #item.data_source="{ item }">
      <v-icon color="disabled">{{
        item.data_source === "file" ? "mdi-file-outline" : "mdi-cloud-outline"
      }}</v-icon>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import { Status, Validation } from "@/lib/definitions/api"
import { getValidation, getValidations } from "@/lib/http/validation"
import SeverityLevelChip from "@/components/SeverityLevelChip.vue"
import { filesize } from "filesize"
import type { VDataTable } from "vuetify/components"

const items = ref<Validation[]>([])
let loading = ref(false)

type ReadonlyHeaders = VDataTable["$props"]["headers"]

const headers: ReadonlyHeaders = [
  { key: "status", title: "Status", width: 1 },
  { key: "data_source", title: "Data source" },
  { key: "api_key_prefix", title: "Submission method" },
  { key: "filename", title: "Filename" },
  { key: "file_size", title: "File size", align: "end" },
  { key: "platform_name", title: "Platform" },
  { key: "cop_version", title: "COP version" },
  { key: "report_code", title: "Report code" },
  { key: "validation_result", title: "Validation result" },
  { key: "stats", title: "Stats" },
  { key: "created", title: "Time" },
]

async function start() {
  loading.value = true
  try {
    items.value = await getValidations()
  } finally {
    loading.value = false
  }
  await checkUnfinished()
}

async function checkUnfinished() {
  let unfinished = items.value.filter(
    (v) => v.status === Status.RUNNING || v.status === Status.WAITING,
  )
  let fetchers = unfinished.map((v) => getValidation(v.id))
  for (let result of await Promise.all(fetchers)) {
    let index = items.value.findIndex((v) => v.id === result.id)
    items.value[index] = result
  }
  unfinished = items.value.filter((v) => v.status === Status.RUNNING || v.status === Status.WAITING)
  if (unfinished.length > 0) {
    setTimeout(checkUnfinished, 1000)
  }
}

onMounted(() => {
  start()
})
</script>
