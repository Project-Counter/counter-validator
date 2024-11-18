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
              v-model="url"
              label="URL"
              :rules="[rules.required]"
            />
          </v-col>
          <!--          <v-col-->
          <!--            cols="12"-->
          <!--            md="4"-->
          <!--          >-->
          <!--            <v-text-field-->
          <!--              v-model="credentials.platform"-->
          <!--              hint="Fill only if required by the server"-->
          <!--              label="Platform"-->
          <!--            />-->
          <!--          </v-col>-->
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
        <h2 class="mb-3">Report selection</h2>
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
              v-model="reportCode"
              label="Report code"
              :items="reportCodes"
            ></v-select>
          </v-col>
        </v-row>

        <v-row>
          <v-col>
            <MonthPicker v-model="beginDate"></MonthPicker>
          </v-col>
          <v-col>
            <MonthPicker v-model="endDate"></MonthPicker>
          </v-col>
        </v-row>
      </v-form>
    </template>

    <template #item.3>
      <v-sheet>
        <h2 class="mb-3">Overview & validation</h2>
        <v-row>
          <v-col>
            <table>
              <tbody>
                <tr>
                  <th>Server URL</th>
                  <td>{{ url }}</td>
                </tr>
                <tr>
                  <th>Credentials</th>
                  <td>{{ credentials }}</td>
                </tr>
                <tr>
                  <th>Report</th>
                  <td>{{ cop }} / {{ reportCode }}</td>
                </tr>
                <tr>
                  <th>Period</th>
                  <td>{{ isoDate(beginDate) }} - {{ isoDate(endDate) }}</td>
                </tr>
              </tbody>
            </table>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-btn
              color="primary"
              @click="create"
              >Validate</v-btn
            >
          </v-col>
        </v-row>
      </v-sheet>
    </template>
  </v-stepper>
</template>

<script setup lang="ts">
import { Credentials } from "@/lib/definitions/api"
import { loadPlatform, loadPlatforms, loadSushiService } from "@/lib/http/platform"
import * as rules from "@/lib/formRules"
import { CoP, ReportCode } from "@/lib/definitions/counter"
import { addMonths, endOfMonth, startOfMonth } from "date-fns"
import { validateCounterAPI } from "@/lib/http/validation"
import { isoDate } from "../lib/datetime"

const stepper = ref(3)
const formValid = ref(false)
const platforms = shallowRef()
const platform = ref(null)
const cop = ref<CoP>("5")
const reportCode = ref<ReportCode>(ReportCode.TR)
const lastMonth = addMonths(new Date(), -1)
const beginDate = ref(startOfMonth(lastMonth))
const endDate = ref(endOfMonth(lastMonth))

const copItems = ["5", "5.1"]
const reportCodes = Object.values(ReportCode)

const loading = ref(false)
const loadingPlatforms = ref(true)

const credentials = reactive<Credentials>({
  customer_id: "aaa",
  requestor_id: "",
  api_key: "",
})
const url = ref("https://sashimi.celus.net/")

// computed
// const availableReports =
// methods
async function update() {
  if (!platform.value) return
  loading.value = true
  const c = await loadSushiService((await loadPlatform(platform.value)).sushi_services[0])
  url.value = c.url
  loading.value = false
}

async function load() {
  loadingPlatforms.value = true
  platforms.value = await loadPlatforms()
  loadingPlatforms.value = false
}

async function create() {
  console.log("create")
  await validateCounterAPI(
    credentials,
    url.value,
    cop.value,
    reportCode.value,
    beginDate.value,
    endDate.value,
  )
}

onMounted(() => {
  load().then()
})
</script>
