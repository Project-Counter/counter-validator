<template>
  <file-upload v-model="files" />

  <div class="text-end">
    <v-btn
      color="primary"
      prepend-icon="mdi-play"
      @click="send"
    >
      Validate
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { ValidationFile } from "@/lib/definitions/ValidationFile"
import { validateFile } from "@/lib/http/validation"

const files: Ref<ValidationFile[]> = ref([])

async function send() {
	for (const file of files.value) {
		file.progress = 50
		await validateFile(file)
		file.progress = 100
	}
}
</script>
