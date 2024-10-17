<template>
  <v-tabs
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
        Validation info
      </h3>
      <v-row
        v-for="(v, k, n) in info"
        :key="k"
        :class="n % 2 ? 'bg-surface-light' : ''"
      >
        <v-col
          cols="12"
          md="2"
        >
          {{ k }}
        </v-col>
        <v-col
          cols="12"
          md="10"
        >
          {{ v }}
        </v-col>
      </v-row>
      <h3 class="my-5">
        Report Header
      </h3>
      <v-row v-if="items?.result?.header?.result">
        <v-col
          cols="12"
          md="2"
        >
          Result
        </v-col>

        <v-col>
          <div
            v-for="(line, idx) in items.result.header.result"
            :key="idx"
          >
            {{ line }}
          </div>
        </v-col>
      </v-row>
      <v-row
        v-if="items?.result?.header?.report"
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
            v-for="(line, key) in items.result.header.report"
            :key="key"
            class="json"
          >
            {{ line }}
          </div>
        </v-col>
      </v-row>
    </v-tabs-window-item>
    <v-tabs-window-item value="result">
      <ValidationMessagesTable :messages="items?.result.messages" />
    </v-tabs-window-item>
  </v-tabs-window>
</template>

<script setup lang="ts">
import { ValidationDetail } from "@/lib/definitions/api"
import { getValidationDetail } from "@/lib/http/validation"
import ValidationMessagesTable from "@/components/ValidationMessagesTable.vue"

const tab = ref(null)

const items = ref<ValidationDetail>()
const route = useRoute()
const info = computed(() => ({
  "File name": items.value?.filename,
  "Created": items.value?.created,
}))

async function load() {
  items.value = await getValidationDetail(route.params.path)
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
