<template>
  <v-dialog
    v-model="dialog"
    activator="parent"
    :max-width="maxWidth"
  >
    <template #default>
      <v-card :title="title">
        <v-card-text class="d-flex flex-column ga-1">
          <slot />
        </v-card-text>

        <v-card-actions>
          <v-btn
            text="Close"
            @click="dialog = false"
          />
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  maxWidth?: number
}>()

const dialog = ref(false)
</script>
