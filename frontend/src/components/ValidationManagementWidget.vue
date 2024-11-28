<template>
  <v-container>
    <v-row>
      <v-col cols="auto">
        <v-btn
          color="primary"
          size="large"
          :to="{ name: '/validation/file' }"
        >
          <v-icon class="me-2"> mdi-file-cog-outline</v-icon>
          Validate a file
        </v-btn>
      </v-col>

      <v-col cols="auto">
        <v-btn
          color="primary"
          size="large"
          :to="{ name: '/validation/api' }"
        >
          <v-icon class="me-2">mdi-server-outline</v-icon>
          Validate API
        </v-btn>
      </v-col>

      <v-spacer></v-spacer>

      <v-col cols="auto">
        <v-btn
          v-if="selected.length > 0"
          color="error"
          size="large"
          :disabled="deleting"
          @click="deleteSelected"
        >
          <v-icon class="me-2">mdi-delete</v-icon>
          Delete selected
          <v-progress-circular
            v-if="deleting"
            size="20"
            :model-value="deleteProgress"
            class="ml-2"
          ></v-progress-circular>
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <ValidationTable
          ref="validationTable"
          v-model:selected="selected"
          selectable
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { deleteValidation } from "@/lib/http/validation"
import { useAppStore } from "@/stores/app"

const selected = ref<string[]>([])
const deleting = ref(false)
const deleteProgress = ref(0)
const validationTable = ref()
const store = useAppStore()

async function deleteSelected() {
  deleting.value = true
  const toDelete = selected.value.length
  let deleted = 0
  for (const id of selected.value) {
    await deleteValidation(id)
    deleted++
    deleteProgress.value = (100 * deleted) / toDelete
  }
  selected.value = []
  deleting.value = false
  store.displayNotification({ message: "Validation(s) were successfully deleted", type: "success" })
  if (validationTable.value) {
    validationTable.value.loadValidations()
  }
}
</script>
