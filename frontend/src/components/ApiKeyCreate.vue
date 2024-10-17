<template>
  <v-dialog
    v-model="dialog"
    activator="parent"
    :max-width="500"
  >
    <template #default>
      <v-form
        v-model="valid"
        @submit.prevent="send"
      >
        <v-card title="Create an API key">
          <v-card-text class="d-flex flex-column ga-1">
            <v-text-field
              v-model="name"
              class="mb-1"
              counter
              label="Name"
              :maxlength="50"
              :rules="[rules.required]"
            />
            <v-text-field
              v-model="expiryDate"
              clearable
              hint="Optional, 00:00 UTC (midnight)"
              label="Expires"
              persistent-clear
              persistent-hint
              type="date"
            />
          </v-card-text>

          <v-card-actions>
            <v-btn
              text="Cancel"
              @click="reset"
            />
            <v-spacer />
            <v-btn
              :disabled="!valid"
              :loading="loading"
              text="Create"
              type="submit"
            />
          </v-card-actions>
        </v-card>
      </v-form>
    </template>
  </v-dialog>
  <v-dialog
    v-model="okDialog"
    :max-width="680"
  >
    <template #default>
      <v-card title="API key created">
        <v-card-text class="px-4 d-flex flex-column ga-6">
          <v-alert
            color="primary"
            icon="mdi-alert"
          >
            Be sure to save this key securely, it won't be displayed again!
          </v-alert>
          <code
            ref="codeRef"
            class="bg-surface-light pa-2 rounded"
            @click="select"
          >{{ okKey }}</code>
          <v-btn
            text="Copy"
            color="primary"
            :prepend-icon="icon ? 'mdi-check' : 'mdi-content-copy'"
            variant="outlined"
            @click="copy"
          />
        </v-card-text>

        <v-card-actions>
          <v-btn
            text="OK"
            @click="okReset"
          />
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>

<script setup lang="ts">
import { Timer } from "@/lib/datetime"
import * as rules from "@/lib/formRules"
import { createApiKey } from "@/lib/http/auth"

const emit = defineEmits(["update"])

// Form + dialogs
const dialog = ref(false)
const valid = ref(false)
const loading = ref(false)
const name = ref("")
const expiryDate = ref(null)

const okDialog = ref(false)
const okKey = ref("")

async function send() {
  loading.value = true
  okKey.value = (await createApiKey(name.value, expiryDate.value))?.key
  loading.value = false
  emit("update")

  name.value = ""
  expiryDate.value = null
  dialog.value = false
  okDialog.value = true
}
function reset() {
  dialog.value = false
  loading.value = false
}
function okReset() {
  okKey.value = ""
  okDialog.value = false
}

// Key selection
const codeRef: Ref<Node | undefined> = ref()
function select() {
  const range = new Range()

  if (!codeRef.value) throw TypeError("codeRef not initialized")
  range.selectNodeContents(codeRef.value)

  const sel = window.getSelection()
  sel?.removeAllRanges()
  sel?.addRange(range)
}

// Key copy
const icon = ref(false)
const iconTimer = new Timer()
async function copy() {
  await navigator.clipboard.writeText(okKey.value)
  icon.value = true
  await iconTimer.sleep(1000)
  icon.value = false
}
</script>
