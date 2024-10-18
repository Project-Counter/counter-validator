<template>
  <v-window>
    <v-window-item>
      <file-picker v-model="files" />
    </v-window-item>
  </v-window>
</template>

<script setup lang="ts">
import { FUpload } from "@/lib/definitions/upload"

const files: Ref<FUpload[]> = ref([])
</script>
