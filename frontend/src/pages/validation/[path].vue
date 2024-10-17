<template>
  <v-tabs
    v-if="validation"
    v-model="tab"
    align-tabs="center"
    color="primary"
    fixed-tabs
  >
    <v-tab
      prepend-icon="mdi-magnify"
      value="details"
    >
      Info
    </v-tab>

    <v-tab
      v-if="validation?.result?.messages"
      prepend-icon="mdi-receipt-text"
      value="result"
    >
      Validation result
    </v-tab>
  </v-tabs>
  <v-tabs-window
    v-model="tab"
    class="mt-5 pa-1"
  >
    <v-tabs-window-item value="details">
      <h3 class="mb-5">
        Basic information
      </h3>
      <ValidationBasicInfo :validation="validation" />

      <section v-if="header">
        <h3 class="my-5">
          Report Header
        </h3>
        <v-row v-if="header.result">
          <v-col
            cols="12"
            md="2"
          >
            Result
          </v-col>

          <v-col>
            <div
              v-for="(line, idx) in (header.result ?? [])"
              :key="idx"
            >
              {{ line }}
            </div>
          </v-col>
        </v-row>
        <v-row
          v-if="header.report"
        >
          <v-col
            cols="12"
            md="2"
          >
            Report header
          </v-col>
          <v-col
            cols="12"
            md="10"
          >
            <div
              v-for="(line, key) in (header.report ?? [])"
              :key="key"
              class="json"
            >
              {{ line }}
            </div>
          </v-col>
        </v-row>
      </section>
    </v-tabs-window-item>
    <v-tabs-window-item
      v-if="validation?.result?.messages"
      value="result"
    >
      <ValidationMessagesTable :messages="validation.result.messages" />
    </v-tabs-window-item>
  </v-tabs-window>
</template>

<script setup lang="ts">
import { ValidationDetail } from "@/lib/definitions/api"
import { getValidationDetail } from "@/lib/http/validation"
import ValidationMessagesTable from "@/components/ValidationMessagesTable.vue"
import ValidationBasicInfo from "@/components/ValidationBasicInfo.vue"

const tab = ref(null)

const validation = ref<ValidationDetail>()
const route = useRoute()

// computed
const header = computed(() => validation.value?.result?.header)

async function load() {
  validation.value = await getValidationDetail(route.params.path)
}
load().then()
</script>

<style scoped lang="scss">
.json {
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 0.875em;
}
</style>
