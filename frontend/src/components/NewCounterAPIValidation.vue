<template>
  <v-stepper
    v-model="stepper"
    :disabled="!formValid"
    :items="['Server selection', 'Endpoint selection', 'Validation']"
    editable
    :max="4"
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
          @update:model-value="selectPlatform"
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
              v-model="url"
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
      </v-form>
    </template>

    <template #item.2>
      <v-form>
        <h2 class="mb-3">Endpoint selection</h2>
        <v-row>
          <v-col>
            <v-select
              v-model="cop"
              label="CoP version"
              :items="copItems"
            ></v-select>
          </v-col>
          <v-col>
            <v-select
              v-model="endpoint"
              :items="apiEndpoints"
              label="Endpoint"
              item-value="code"
              item-title="name"
              return-object
            >
              <template #item="{ item, props }">
                <v-list-item
                  v-bind="props"
                  :subtitle="item.raw.path"
                >
                </v-list-item>
              </template>
            </v-select>
          </v-col>
        </v-row>

        <v-row v-if="reportEndpoint">
          <v-col
            cols="6"
            md="3"
            lg="2"
          >
            <v-select
              v-model="reportCode"
              label="Report code"
              :items="reportCodes"
            ></v-select>
          </v-col>
          <v-col cols="12">
            <MonthRangePicker
              v-model:start="beginDate"
              v-model:end="endDate"
            />
          </v-col>
        </v-row>
        <v-row v-if="reportEndpoint && availableAttributes.length">
          <v-col
            cols="auto"
            class="font-weight-light align-self-center text-center"
          >
            Attributes to show
            <br />
            <v-btn
              size="small"
              variant="tonal"
              class="mr-1"
              @click="attributesToShow = availableAttributes"
            >
              All
            </v-btn>
            <v-btn
              size="small"
              variant="tonal"
              @click="attributesToShow = []"
            >
              None
            </v-btn>
          </v-col>
          <v-col class="d-flex flex-1-1-0 align-self-center flex-wrap">
            <span
              v-for="attr in availableAttributes"
              :key="attr"
            >
              <v-checkbox
                v-model="attributesToShow"
                :label="attr"
                :value="attr"
                density="compact"
                class="pr-5"
                hide-details
              />
            </span>
          </v-col>
        </v-row>
        <v-row v-if="reportEndpoint && availableAttributes.length">
          <v-col
            cols="auto"
            class="font-weight-light align-self-center text-center"
          >
            Filters
          </v-col>
          <v-col>
            <v-select
              v-if="selectedReportInfo?.metrics"
              v-model="multiValueFilters['Metric_Type']"
              :items="selectedReportInfo.metrics"
              label="Metric_Type"
              clearable
              multiple
              :hide-details="true"
              min-width="320px"
            />
            <template
              v-for="attr in availableAttributes"
              :key="attr"
            >
              <v-select
                v-if="possibleAttributeValues(cop, attr)"
                v-model="multiValueFilters[attr]"
                :items="possibleAttributeValues(cop, attr)"
                :label="attr"
                clearable
                multiple
                :hide-details="true"
                min-width="320px"
              />
              <v-text-field
                v-else
                v-model="textFilters[attr]"
                :label="attr"
                outlined
                clearable
                multiple
                :hide-details="true"
                min-width="320px"
              />
            </template>
          </v-col>
        </v-row>
      </v-form>
    </template>

    <template #item.3>
      <v-sheet>
        <h2 class="mb-3">Validation</h2>
        <v-row>
          <v-col>
            <v-table density="compact">
              <tbody>
                <tr>
                  <th>Server URL</th>
                  <td>{{ url }}</td>
                </tr>
                <tr>
                  <th>Credentials</th>
                  <td>
                    <table class="overview dense">
                      <tr
                        v-for="(v, k) in credentials"
                        :key="k"
                      >
                        <th class="font-weight-regular">{{ k }}</th>
                        <td>{{ v || "-" }}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <th>API endpoint</th>
                  <td>{{ endpoint.path }}</td>
                </tr>
                <tr v-if="reportEndpoint">
                  <th>Report</th>
                  <td>{{ cop }} / {{ reportCode }}</td>
                </tr>
                <tr v-if="reportEndpoint">
                  <th>Period</th>
                  <td>{{ isoDate(beginDate) }} - {{ isoDate(endOfMonth(endDate)) }}</td>
                </tr>
                <tr v-if="reportEndpoint">
                  <th>Attributes to show</th>
                  <td>
                    <v-chip
                      v-for="a in attributesToShow"
                      :key="a"
                      class="mt-1 mr-1"
                    >
                      {{ a }}
                    </v-chip>
                  </td>
                </tr>
                <tr v-if="reportEndpoint">
                  <th>Filters</th>
                  <td>
                    <table class="overview dense">
                      <tr
                        v-for="(v, k) in filters"
                        :key="k"
                      >
                        <th class="font-weight-regular">{{ k }}</th>
                        <td>{{ v || "-" }}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-col>
        </v-row>
      </v-sheet>
    </template>

    <template #next>
      <v-btn
        v-if="stepper < 3"
        @click="stepper++"
        >Next</v-btn
      >
      <v-btn
        v-else
        color="primary"
        :disabled="false"
        :loading="creatingValidation"
        @click="create"
        >Validate</v-btn
      >
    </template>
  </v-stepper>
</template>

<script setup lang="ts">
import { CounterAPIEndpoint, Credentials } from "@/lib/definitions/api"
import { loadPlatform, loadPlatforms, loadSushiService } from "@/lib/http/platform"
import * as rules from "@/lib/formRules"
import { CoP, getReportInfo, ReportCode, possibleAttributeValues } from "@/lib/definitions/counter"
import { addMonths, endOfMonth, startOfMonth } from "date-fns"
import { validateCounterAPI } from "@/lib/http/validation"
import { useAppStore } from "@/stores/app"
import { isoDate } from "@/lib/formatting"

// housekeeping
const stepper = ref(1)
const formValid = ref(false)
const loading = ref(false)
const loadingPlatforms = ref(true)
const store = useAppStore()
const router = useRouter()
const creatingValidation = ref(false)
const platforms = shallowRef()

// credentials and related select options
const platform = ref(null)

const cop = ref<CoP>("5")
const copItems: CoP[] = ["5", "5.1"]

const url = ref("https://sashimi.celus.net/")

const reportCode = ref<ReportCode>(ReportCode.TR)
const reportCodes = Object.values(ReportCode)

const lastMonth = addMonths(new Date(), -1)
const beginDate = ref(startOfMonth(lastMonth))
const endDate = ref(endOfMonth(lastMonth))

const credentials = reactive<Credentials>({
  customer_id: "aaa",
  requestor_id: "",
  api_key: "",
})

const apiEndpoints: { name: string; path: CounterAPIEndpoint; code: string }[] = [
  { name: "Report", path: "/reports/[id]", code: "reports" },
  { name: "Report list", path: "/reports", code: "report-list" },
  { name: "Members", path: "/members", code: "members" },
  { name: "Status", path: "/status", code: "status" },
]
const endpoint = ref(apiEndpoints[0])
const reportEndpoint = computed(() => endpoint.value.code === "reports")

const selectedReportInfo = computed(() => {
  if (!reportEndpoint.value) return null
  return getReportInfo(cop.value, reportCode.value)
})

const attributesToShow = ref([])
const availableAttributes = computed<string[]>(() => {
  if (selectedReportInfo.value) return selectedReportInfo.value.attributes
  return []
})

watch(reportCode, () => {
  // when report code changes, reset attributes to show
  attributesToShow.value = []
})

// filters
const multiValueFilters = ref<{ [key: string]: string[] }>({})
const textFilters = ref<{ [key: string]: string }>({})
const filters = computed(() => {
  return { ...multiValueFilters.value, ...textFilters.value }
})

// methods for API communication
async function selectPlatform() {
  if (!platform.value) return
  loading.value = true
  const c = await loadSushiService((await loadPlatform(platform.value)).sushi_services[0])
  url.value = c.url
  loading.value = false
}

async function loadPlatformData() {
  loadingPlatforms.value = true
  platforms.value = await loadPlatforms()
  loadingPlatforms.value = false
}

async function create() {
  creatingValidation.value = true
  let extra: Record<string, string> = {}

  // encode attributes to show and filters
  if (reportEndpoint.value) {
    if (attributesToShow.value.length > 0) {
      extra["attributes_to_show"] = attributesToShow.value.join("|")
    }
    Object.entries(multiValueFilters.value).forEach(([k, v]) => {
      if (v && v.length) {
        extra[k.toLowerCase()] = v.join("|")
      }
    })
    Object.entries(textFilters.value).forEach(([k, v]) => {
      if (v && v.length) {
        extra[k.toLowerCase()] = v
      }
    })
  }

  try {
    await validateCounterAPI(
      credentials,
      url.value,
      cop.value,
      endpoint.value.path,
      reportEndpoint.value ? reportCode.value : undefined,
      reportEndpoint.value ? beginDate.value : undefined,
      reportEndpoint.value ? endDate.value : undefined,
      extra,
    )
  } catch (err) {
    console.error(err)
    return
  } finally {
    creatingValidation.value = false
  }
  store.displayNotification({ message: "Validation was successfully started", type: "success" })
  await router.push({ name: "/" })
}

onMounted(loadPlatformData)
</script>
