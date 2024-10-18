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
            @click="showUploadDialog = true"
          >
            <v-icon class="me-1"> mdi-file-cog-outline </v-icon>
            Validate a file
          </v-btn>
        </v-col>
      </v-row>
    </template>

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
      <router-link :to="item.id + '/'">
        {{ item.filename }}
      </router-link>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import { Validation } from "@/lib/definitions/api"
import { getValidations } from "@/lib/http/validation"
import ValidationResult from "@/components/ValidationResultChip.vue"

const items = ref<Validation[]>([])
const showUploadDialog = ref(false)

const headers = [
  { key: "status", title: "Status", width: 1 },
  { key: "filename", title: "Filename" },
  { key: "platform_name", title: "Platform" },
  { key: "validation_result", title: "Validation Result" },
  { key: "id", title: "Time" },
]

async function load() {
  items.value = await getValidations()
  // postprocess validations to put name into platform_name for all cases
  items.value.forEach((val) => {
    val.platform_name = val.platform_name ?? val.platform
  })
}
load().then()
</script>
