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

    <v-tab prepend-icon="mdi-chart-bar">Statistics</v-tab>

    <v-tab
      v-if="Object.keys(validation.stats).length"
      prepend-icon="mdi-receipt-text"
      value="messages"
    >
      Validation messages
    </v-tab>
  </v-tabs>
  <v-tabs-window v-model="tab">
    <v-tabs-window-item value="details">
      <v-container>
        <v-row>
          <v-col v-bind="colAttrs">
            <v-card v-bind="cardAttrs">
              <v-card-title>Basic information</v-card-title>
              <v-card-text>
                <!-- ts need the v-if bellow to narrow down the type -->
                <ValidationBasicInfo
                  v-if="validation"
                  :validation="validation"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!--
          without cop_version, the extracted info would be empty anyway
          this happens for errors or non-report api endpoints
         -->
        <v-row v-if="validation?.cop_version">
          <v-col v-bind="colAttrs">
            <v-card v-bind="cardAttrs">
              <v-card-title>Extracted information</v-card-title>
              <v-card-text>
                <ValidationExtractedInfo
                  v-if="validation"
                  :validation="validation"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-if="header?.report">
          <v-col v-bind="colAttrs">
            <v-card
              v-if="header"
              v-bind="cardAttrs"
            >
              <v-card-title>Report Header</v-card-title>
              <v-card-text v-if="header.format === 'tabular'">
                <table class="src">
                  <tbody>
                    <tr
                      v-for="(row, idx) in tableHeader"
                      :key="idx"
                    >
                      <th>{{ row[0] }}</th>
                      <td>{{ row[1] }}</td>
                    </tr>
                  </tbody>
                </table>
              </v-card-text>
              <v-card-text v-else>
                <div
                  v-for="(line, key) in header.report ?? []"
                  :key="key"
                  class="json"
                >
                  {{ line }}
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-tabs-window-item>

    <v-tabs-window-item value="statistics">
      <v-container>
        <ValidationMessageStatsTable
          v-if="validation"
          :validation="validation"
          @select-message="selectMessage"
        />
      </v-container>
    </v-tabs-window-item>

    <v-tabs-window-item
      value="messages"
      eager
    >
      <v-container>
        <ValidationMessagesTable
          v-if="validation"
          ref="messagesComponent"
          :validation="validation"
        />
      </v-container>
    </v-tabs-window-item>
  </v-tabs-window>
</template>

<script setup lang="ts">
import { Message, ValidationDetail } from "@/lib/definitions/api"
import { getValidationDetail } from "@/lib/http/validation"
import ValidationMessagesTable from "@/components/ValidationMessagesTable.vue"

const tab = ref("info")

const validation = ref<ValidationDetail>()
const route = useRoute()

// styles
const cardAttrs = {
  elevation: 3,
  class: "pa-4",
}
const colAttrs = {
  cols: "12",
  lg: "10",
  xl: "8",
  xxl: "6",
  "offset-lg": "1",
  "offset-xl": "2",
  "offset-xxl": "3",
}

// computed
const header = computed(() => validation.value?.result_data?.header)

const tableHeader = computed(() => {
  if (!header.value || header.value.format !== "tabular") return []

  let out = []
  for (let i = 1; i < 100; i++) {
    let a = header.value.report[`A${i}`] || ""
    let b = header.value.report[`B${i}`] || ""
    if (a === "" && b === "") {
      break
    }
    out.push([a, b])
  }
  return out
})

async function load() {
  if ("id" in route.params) {
    // check needed for TS to narrow down the type
    validation.value = await getValidationDetail(route.params.id)
  }
}

// message selected in the stats table
const messagesComponent = ref<InstanceType<typeof ValidationMessagesTable>>()

function selectMessage(message: Message) {
  if (messagesComponent.value) {
    messagesComponent.value.applyFilterByMessage(message)
    tab.value = "messages"
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.json {
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 0.875em;
  color: #555555;
}

table.src {
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 0.875em;
  color: #555555;

  th {
    font-weight: bold;
    text-align: left;
    padding-right: 1rem;
  }
}
</style>
