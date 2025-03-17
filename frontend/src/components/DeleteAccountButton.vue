<template>
  <v-dialog
    v-model="dialog"
    max-width="640"
  >
    <template #activator="{ props }">
      <v-btn
        v-bind="{ ...props, ...$attrs }"
        color="error"
        variant="tonal"
      >
        <v-icon>mdi-delete</v-icon>
        Delete account
      </v-btn>
    </template>
    <v-card>
      <v-card-title>Delete account</v-card-title>
      <v-card-text>
        <v-icon
          color="error"
          class="mr-2"
          size="large"
          >mdi-alert-circle-outline</v-icon
        >
        Are you sure you want to delete your account and all your data? This action is irreversible.
      </v-card-text>
      <v-card-actions class="ma-2">
        <v-btn @click="dialog = false">Cancel</v-btn>
        <v-btn
          color="error"
          @click="deleteAccount"
        >
          <v-icon>mdi-delete</v-icon>
          Delete
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup lang="ts">
const dialog = ref(false)

const emit = defineEmits(["delete"])

async function deleteAccount() {
  emit("delete")
  dialog.value = false
}
</script>
