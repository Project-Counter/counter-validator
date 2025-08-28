<template>
  <v-container v-if="publicView">
    <v-row>
      <v-col v-bind="colAttrs">
        <v-alert
          color="info"
          icon="mdi-information"
        >
          This is a public view of the validation. Some information may be hidden.
        </v-alert>
      </v-col>
    </v-row>
  </v-container>

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
      v-if="finished"
      prepend-icon="mdi-chart-bar"
      >Statistics</v-tab
    >

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
        <v-row v-if="!finished">
          <v-col v-bind="colAttrs">
            <v-card v-bind="cardAttrs">
              <v-card-text v-if="inProgress">
                <v-progress-circular
                  indeterminate
                  color="primary"
                  class="me-4"
                />
                The validation is still running. Please check back later.
              </v-card-text>
              <v-card-text v-else>
                <v-alert type="error">
                  The validation failed. Here are the details:

                  <div class="overflow-auto pt-4">
                    <pre>{{ validation.error_message }}</pre>
                  </div>
                </v-alert>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col v-bind="colAttrs">
            <v-card v-bind="cardAttrs">
              <v-card-title>
                Basic information

                <v-tooltip
                  location="bottom"
                  max-width="600px"
                >
                  <template #activator="{ props }">
                    <v-btn
                      v-if="!publicView && finished"
                      class="float-end ms-4"
                      color="primary"
                      variant="flat"
                      v-bind="props"
                      :href="`/api/v1/validations/validation/${validation.id}/export`"
                    >
                      <v-icon class="me-2">mdi-download</v-icon>
                      Export
                    </v-btn>
                  </template>
                  Export the validation as an Excel file
                </v-tooltip>

                <v-tooltip
                  location="bottom"
                  max-width="600px"
                >
                  <template #activator="{ props }">
                    <v-btn
                      v-if="validation && validation.data_source === 'counter_api' && !publicView"
                      class="float-end"
                      color="secondary"
                      variant="flat"
                      v-bind="props"
                      @click="repeatValidation"
                    >
                      <v-icon class="me-2">mdi-refresh</v-icon>
                      Repeat validation
                    </v-btn>
                  </template>
                  Open a new validation wizard with data pre-populated from this validation.
                </v-tooltip>
              </v-card-title>
              <v-card-text>
                <!-- ts need the v-if bellow to narrow down the type -->
                <ValidationBasicInfo
                  v-if="validation"
                  :validation="validation"
                  :public-view="publicView"
                  @expiration-date-updated="updateExpirationDate"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!--
          without cop_version or for non-report api endpoints,
          the extracted info would be empty anyway
         -->
        <v-row v-if="hasExtractedInfo">
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
              <v-card-text v-if="reportinfo?.format === 'tabular'">
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
        <v-row>
          <v-col v-bind="colAttrs">
            <v-card v-bind="cardAttrs">
              <v-card-text>
                <ValidationMessageStatsTable
                  v-if="validation && !isEmpty(validation.stats)"
                  :validation="validation"
                  :public-view="publicView"
                  @select-message="selectMessage"
                />
                <div v-else-if="validation">
                  Everything looks good! No validation messages to show.

                  <div class="text-h2 text-center py-14">
                    Good job
                    <v-icon
                      color="success"
                      size="x-small"
                      class="mb-4"
                      >mdi-thumb-up-outline</v-icon
                    >
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-tabs-window-item>

    <v-tabs-window-item
      value="messages"
      eager
    >
      <v-container fluid>
        <v-card v-bind="cardAttrs">
          <v-card-text>
            <ValidationMessagesTable
              v-if="validation"
              ref="messagesComponent"
              :validation="validation"
              :public-view="publicView"
            />
          </v-card-text>
        </v-card>
      </v-container>
    </v-tabs-window-item>
  </v-tabs-window>
</template>

<script setup lang="ts">
import { Message, Status, ValidationDetail } from "@/lib/definitions/api"
import ValidationMessagesTable from "@/components/ValidationMessagesTable.vue"
import { isEmpty } from "lodash"

const props = withDefaults(
  defineProps<{
    validation: ValidationDetail
    publicView?: boolean
  }>(),
  {
    publicView: false,
  },
)

const tab = ref("info")

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
const reportinfo = computed(() => props.validation?.result_data?.reportinfo)
const header = computed(() => props.validation?.result_data?.header)

const tableHeader = computed(() => {
  if (!reportinfo.value || reportinfo.value.format !== "tabular" || !header.value) return []

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

const finished = computed(() => {
  return props.validation?.status === Status.SUCCESS
})

const inProgress = computed(() => {
  return props.validation?.status === Status.RUNNING || props.validation?.status === Status.WAITING
})

const hasExtractedInfo = computed(() => {
  return (
    props.validation?.cop_version &&
    (props.validation?.api_endpoint === "/reports/[id]" || props.validation?.data_source === "file")
  )
})

// message selected in the stats table
const messagesComponent = ref<InstanceType<typeof ValidationMessagesTable>>()

function selectMessage(message: Message) {
  if (messagesComponent.value) {
    messagesComponent.value.applyFilterByMessage(message)
    tab.value = "messages"
  }
}

// repeat validation
const router = useRouter()
function repeatValidation() {
  router.push({
    path: "/validation/api",
    query: { base: props.validation.id },
  })
}

const emit = defineEmits<{
  (e: "expiration-date-updated", expirationDate: string): void
}>()

function updateExpirationDate(expirationDate: string) {
  emit("expiration-date-updated", expirationDate)
}
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
