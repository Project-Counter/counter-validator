<template>
  <v-stepper
    v-model="stepper"
    :disabled="!formValid"
    :items="['Server selection', 'Report selection', 'Download & validation']"
    :mobile="null"
  >
    <template #item.1>
      <v-form
        v-model="formValid"
        :disabled="loading"
      >
        <h2 class="mb-3">Server</h2>
        <v-autocomplete
          v-model="platform"
          clearable
          hint="Type to search in the COUNTER Registry"
          item-subtitle="abbrev"
          item-title="name"
          item-value="id"
          :items="platforms"
          label="Search in platforms"
          :loading="loadingPlatforms"
          persistent-clear
          persistent-hint
          prepend-inner-icon="mdi-magnify"
          @update:model-value="update"
        />
        <div class="my-3">
          <v-divider>or enter manually</v-divider>
        </div>
        <v-row dense>
          <v-col
            cols="12"
            md="8"
          >
            <v-text-field
              v-model="credentials.url"
              label="URL"
              :rules="[rules.required]"
            />
          </v-col>
          <v-col
            cols="12"
            md="4"
          >
            <v-text-field
              v-model="credentials.platform"
              hint="Fill only if required by the server"
              label="Platform"
            />
          </v-col>
        </v-row>

        <h2 class="mt-4 mb-3">Credentials</h2>
        <v-row dense>
          <v-col
            cols="12"
            md="4"
          >
            <v-text-field
              v-model="credentials.customer_id"
              label="Customer ID"
              :rules="[rules.required]"
            />
          </v-col>
          <v-col
            cols="12"
            md="4"
          >
            <v-text-field
              v-model="credentials.requestor_id"
              hint="Fill only if required by the server"
              label="Requestor ID"
            />
          </v-col>
          <v-col
            cols="12"
            md="4"
          >
            <v-text-field
              v-model="credentials.api_key"
              hint="Fill only if required by the server"
              label="API key"
            />
          </v-col>
        </v-row>

        <!--        <div class="text-end my-5 ">-->
        <!--          <v-btn-->
        <!--            class="ma-2"-->
        <!--            prepend-icon="mdi-help-circle-outline"-->
        <!--          >-->
        <!--            Get status-->
        <!--          </v-btn>-->
        <!--          <v-btn-->
        <!--            class="ma-2"-->
        <!--            prepend-icon="mdi-account-multiple"-->
        <!--          >-->
        <!--            Get members-->
        <!--          </v-btn>-->
        <!--        </div>-->
      </v-form>
    </template>
  </v-stepper>
</template>

<script setup lang="ts">
import { Credentials } from "@/lib/definitions/api"
import { loadPlatform, loadPlatforms, loadSushiService } from "@/lib/http/platform"
import * as rules from "@/lib/formRules"

const stepper = ref(0)
const formValid = ref(false)
const platforms = shallowRef()
const platform = ref(null)
// const sushiService = reactive<SushiService>({
//   id: "",
//   counter_release: "",
//   url: "",
//   ip_address_authorization: undefined,
//   api_key_required: undefined,
//   platform_attr_required: undefined,
//   requestor_id_required: undefined,
//   deprecated: false,
// })
const loading = ref(false)
const loadingPlatforms = ref(true)

const credentials = reactive<Credentials>({
  url: "",
  platform: "",
  customer_id: "",
  requestor_id: "",
  api_key: "",
})

async function update() {
  if (!platform.value) return
  loading.value = true
  const c = await loadSushiService((await loadPlatform(platform.value)).sushi_services[0])
  credentials.url = c.url
  loading.value = false
}

async function load() {
  loadingPlatforms.value = true
  platforms.value = await loadPlatforms()
  loadingPlatforms.value = false
}

// async function submit() {
//   await validateSushi(credentials)
// }

// watch(stepper, submit)

load().then()
</script>
