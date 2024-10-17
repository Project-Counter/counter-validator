<template>
  <v-window v-model="window">
    <v-window-item>
      <file-picker v-model="files" />

      <div class="text-end">
        <v-slide-x-transition>
          <v-btn
            v-if="files.length > 0"
            text="Validate"
            color="primary"
            @click="window = 1"
          />
        </v-slide-x-transition>
      </div>
    </v-window-item>
    <v-window-item>
      <file-uploader
        v-if="window == 1"
        :files="files"
        @back="back"
      />
    </v-window-item>
  </v-window>
</template>

<script setup lang="ts">
import { FUpload } from "@/lib/definitions/upload"

const window = ref(1)

const files: Ref<FUpload[]> = ref([])

function back() {
  files.value.length = 0
  window.value = 0
}

</script>
