<template>
  <v-sheet
    border="dashed lg"
    class="d-flex flex-column align-center text-center pt-4 pb-6 position-relative"
    @dragleave.prevent="overlay = false"
    @dragover.stop.prevent="overlay = true"
    @drop.stop.prevent="onDrop"
  >
    <v-icon
      icon="mdi-cloud-upload"
      size="64"
    />
    <span class="text-h5 mb-2">Add files for validation</span>
    <span>Drag and drop</span>
    <span class="text-caption mb-1 text-medium-emphasis">or</span>
    <v-btn
      prepend-icon="mdi-plus"
      size="small"
      text="add files"
      variant="tonal"
      @click="inputRef.click()"
    />

    <span class="text-caption mt-2 text-medium-emphasis"
      >Supported formats: json, csv, tsv, ods, xlsx, xls</span
    >

    <input
      ref="inputRef"
      class="d-none"
      multiple
      type="file"
      @change="onPick"
    />
    <v-overlay
      contained
      :model-value="overlay"
      scrim
    />
  </v-sheet>
  <div class="d-flex flex-column ga-3 my-3">
    <v-slide-x-transition group>
      <v-sheet
        v-for="(item, index) in model"
        :key="item.file.name"
        border
        class="pa-3"
        rounded
      >
        <v-row no-gutters>
          <v-col
            :cols="12"
            :sm="6"
          >
            <div class="text-truncate mb-2 pr-2">
              <v-btn
                density="comfortable"
                icon="mdi-close"
                variant="text"
                @click="removeFile(index)"
              />
              {{ item.file.name }}
            </div>
          </v-col>
          <v-col
            :cols="12"
            :sm="6"
          >
            <v-combobox
              v-model="item.platform"
              append-inner-icon="mdi-content-copy"
              auto-select-first="exact"
              clearable
              density="compact"
              hide-details
              item-subtitle="abbrev"
              item-title="name"
              item-value="id"
              :items="platforms"
              label="Platform"
              :loading
              persistent-clear
              prepend-inner-icon="mdi-magnify"
              return-object
              @click:append-inner="copyPlatform(item)"
            />
            <ul
              v-if="index == 0"
              class="ml-4 text-caption text-medium-emphasis"
            >
              <li>optional, type to search or write custom text for yourself</li>
              <li>click <v-icon icon="mdi-content-copy" /> to copy to all other files</li>
            </ul>
          </v-col>
        </v-row>
      </v-sheet>
    </v-slide-x-transition>
  </div>
</template>

<script setup lang="ts">
import { FUpload } from "@/lib/definitions/upload"
import { loadPlatforms } from "@/lib/http/platform"

const model = defineModel<FUpload[]>({ required: true })

const inputRef = ref()
const overlay = ref(false)
const platforms = shallowRef()
const loading = ref(true)

async function load() {
  loading.value = true
  platforms.value = await loadPlatforms()
  loading.value = false
}
function addFiles(files: Iterable<File>) {
  for (const file of files) {
    if (!model.value.some((f) => f.file.name === file.name)) {
      model.value.push({ file })
    }
  }
}
function removeFile(index: number) {
  model.value.splice(index, 1)
}
function onPick(e: Event) {
  const target = e.target as HTMLInputElement
  addFiles(target.files ?? [])
}
function onDrop(e: DragEvent) {
  overlay.value = false
  addFiles(e.dataTransfer?.files ?? [])
}
function copyPlatform(item: FUpload) {
  for (const rec of model.value) {
    rec.platform = item.platform
  }
}

load().then()
</script>
