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
      :disabled="uploading"
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
        <v-row>
          <v-col
            :cols="12"
            :sm="6"
          >
            <div class="text-truncate">
              <v-btn
                density="comfortable"
                icon="mdi-close"
                variant="text"
                :disabled="uploading"
                @click="removeFile(index)"
              />
              {{ item.file.name }}
              <v-chip
                size="small"
                variant="plain"
                >{{ filesize(item.file.size) }}</v-chip
              >
            </div>
            <v-progress-linear
              v-if="justUploading === item"
              color="primary"
              height="4"
              indeterminate
            />
            <div
              v-if="item.err"
              class="text-caption text-error"
            >
              <v-icon>mdi-alert-circle-outline</v-icon>
              {{ item.err }}
            </div>
          </v-col>
          <v-col
            :cols="12"
            :sm="6"
          >
            <v-text-field
              v-model="item.user_note"
              append-inner-icon="mdi-content-copy"
              auto-select-first="exact"
              clearable
              density="compact"
              hide-details
              label="Note"
              :disabled="uploading"
              @click:append-inner="copyNote(item)"
            />
          </v-col>
        </v-row>
      </v-sheet>
    </v-slide-x-transition>

    <div class="text-end">
      <v-slide-x-transition>
        <v-btn
          v-if="model.length > 0"
          color="primary"
          text="Validate"
          :disabled="uploading"
          @click="startUploading"
        />
      </v-slide-x-transition>
    </div>
    <div v-if="anyError && !justUploading">
      <v-alert type="error">
        There were errors during the data upload. Files for which errors occurred will not be shown
        amongst your validations.
      </v-alert>
      <div class="text-end pt-4">
        <v-btn
          :to="{ name: '/' }"
          color="secondary"
          >Go to validations</v-btn
        >
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FUpload } from "@/lib/definitions/upload"
import { validateFile } from "@/lib/http/validation"
import { filesize } from "filesize"
import { HttpStatusError } from "@/lib/http/util"

const model = defineModel<FUpload[]>({ required: true })

const inputRef = ref()
const overlay = ref(false)
const uploading = ref(false)
const justUploading = ref<FUpload | null>(null)
const router = useRouter()
const anyError = ref(false)

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
function copyNote(item: FUpload) {
  for (const rec of model.value) {
    rec.user_note = item.user_note
  }
}

async function upload(file: FUpload) {
  try {
    await validateFile(file)
  } catch (err) {
    if (err instanceof HttpStatusError && err.res?.status === 400) {
      const data = await err.res?.json()
      if (data.file) file.err = data.file.join("; ")
    } else if (err instanceof HttpStatusError && err.res?.status === 413) {
      file.err = "The uploaded file is too large"
    } else {
      file.err = `${err}`
    }
    anyError.value = true
  }
}

async function startUploading() {
  uploading.value = true
  try {
    for (const file of model.value) {
      justUploading.value = file
      await upload(file)
      justUploading.value = null
    }
  } finally {
    if (!anyError.value) {
      await router.push("/validation/")
    }
  }
}
</script>
