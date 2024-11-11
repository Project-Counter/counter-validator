<template>
  <v-data-table
    :headers="headers"
    :items="items"
    :mobile="null"
    no-data-text="No validations in your history"
  >
    <template #top>
      <v-row>
        <v-col>
          <v-btn
            color="primary"
            size="large"
            :to="{ name: '/validation/file' }"
          >
            <v-icon class="me-2"> mdi-file-cog-outline </v-icon>
            Validate a file
          </v-btn>
        </v-col>
      </v-row>
    </template>

    <template #item.status="{ item }">
      <validation-status :validation="item" />
    </template>

    <template #item.validation_result="{ item }">
      <ValidationResult :item="item" />
    </template>

    <template #item.created="{ item }">
      <date-tooltip :date="item.created" />
    </template>

    <template #item.filename="{ item }">
      <router-link :to="'validation/' + item.id + '/'">
        {{ item.filename }}
      </router-link>
    </template>

    <template #item.file_size="{ item }">
      {{ filesize(item.file_size) }}
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import { Validation } from "@/lib/definitions/api"
import { getValidations } from "@/lib/http/validation"
import ValidationResult from "@/components/ValidationResultChip.vue"
import { filesize } from "filesize"
import type { VDataTable } from "vuetify/components"

const items = ref<Validation[]>([])

type ReadonlyHeaders = VDataTable["$props"]["headers"]

const headers: ReadonlyHeaders = [
  { key: "status", title: "Status", width: 1 },
  { key: "filename", title: "Filename" },
  { key: "file_size", title: "File size", align: "end" },
  { key: "platform_name", title: "Platform" },
  { key: "validation_result", title: "Validation result" },
  { key: "created", title: "Time" },
]

async function load() {
  items.value = await getValidations()
}
load().then()
</script>
