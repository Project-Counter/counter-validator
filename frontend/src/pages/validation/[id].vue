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
      v-if="validation && Object.keys(validation.stats).length"
      prepend-icon="mdi-receipt-text"
      value="result"
    >
      Validation messages
    </v-tab>
  </v-tabs>
  <v-tabs-window
    v-model="tab"
    class="mt-5 pa-1"
  >
    <v-tabs-window-item value="details">
      <h3 class="mb-5">Basic information</h3>
      <!-- ts need the v-if bellow to narrow down the type -->
      <ValidationBasicInfo
        v-if="validation"
        :validation="validation"
      />

      <h3 class="mt-6 mb-5">Extracted information</h3>
      <ValidationExtractedInfo
        v-if="validation"
        :validation="validation"
      />

      <section v-if="header">
        <h3 class="my-5">Report Header</h3>
        <div
          v-for="(line, key) in header.report ?? []"
          :key="key"
          class="json"
        >
          {{ line }}
        </div>
      </section>
    </v-tabs-window-item>

    <v-tabs-window-item
      v-if="validation"
      value="result"
    >
      <ValidationMessagesTable :validation="validation" />
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
const header = computed(() => validation.value?.result_data?.header)

async function load() {
  if ("id" in route.params) {
    // check needed for TS to narrow down the type
    validation.value = await getValidationDetail(route.params.id)
  }
}
load().then()
</script>

<style scoped lang="scss">
.json {
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 0.825em;
  color: #555555;
}
</style>
