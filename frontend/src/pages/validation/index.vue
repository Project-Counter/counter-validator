<template>
  <v-data-table
    :headers="headers"
    :items="items"
    :mobile="null"
    no-data-text="No validations in your history"
  >
    <template #item.status="{ value }">
      <validation-status :value="value" />
    </template>

    <template #item.validation_result="{ item }">
      <ValidationResult :item="item" />
    </template>

    <template #item.id="{ item }">
      <date-tooltip :date="item.created" />
    </template>

    <template #item.filename="{ item }">
      <router-link
        :to="item.id + '/'"
      >
        {{ item.filename }}
      </router-link>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import { Validation } from "@/lib/definitions/api"
import { getValidations } from "@/lib/http/validation"
import ValidationResult from "@/components/ValidationResultChip.vue"

const compare = new Intl.Collator().compare

const items = ref<Validation[]>([])
const headers = [
  { key: "status", title: "Status", width: 1 },
  { key: "validation_result", title: "Validation Result" },
  { key: "filename", title: "Filename" },
  { key: "platform", title: "Platform", sortRaw(a: Validation, b: Validation) {
    const platformA = a.platform ?? a.platform_name
    const platformB = b.platform ?? b.platform_name
    return compare(platformA, platformB)
  } },
  { key: "id", title: "Time" },
]

async function load() {
  items.value = await getValidations()
}
load().then()
</script>
