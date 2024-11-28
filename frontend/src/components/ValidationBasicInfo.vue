<template>
  <table class="overview ml-4">
    <tbody>
      <tr>
        <th>Filename</th>
        <td>
          <a
            target="_blank"
            :href="validation.file_url"
            >{{ validation?.filename }}</a
          >
          ({{ filesize(validation.file_size) }})
        </td>
      </tr>
      <tr>
        <th>Created</th>
        <td>{{ validation?.created }} ({{ relCreated }})</td>
      </tr>
      <tr>
        <th>Task status</th>
        <td>
          {{ validation && (statusMap.get(validation.status) ?? "Unknown") }}
        </td>
      </tr>
      <tr>
        <th>Validation result</th>
        <td>
          <SeverityLevelChip :severity="validation.validation_result" />
        </td>
      </tr>
    </tbody>
  </table>

  <h3
    v-if="validation.credentials"
    class="text-h6 mt-4 mb-2"
  >
    Requested COUNTER API parameters
  </h3>
  <table
    v-if="validation.credentials"
    class="overview ml-4"
  >
    <tbody>
      <tr>
        <th>Credentials</th>
        <td>
          <table class="dense">
            <tr
              v-for="(value, key) in validation.credentials"
              :key="key"
            >
              <th class="font-weight-regular">{{ key }}</th>
              <td>{{ value }}</td>
            </tr>
          </table>
        </td>
      </tr>
      <tr
        v-for="attr in sushiAttrs"
        :key="attr.attr"
      >
        <th>{{ attr.name }}</th>
        <td v-if="typeof validation[attr.attr] === 'object'">
          <table class="dense">
            <tr
              v-for="(value, key) in validation[attr.attr]"
              :key="key"
            >
              <th class="font-weight-regular">{{ key }}</th>
              <td>{{ stringify(value) }}</td>
            </tr>
          </table>
        </td>
        <td v-else>{{ stringify(validation[attr.attr]) }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import { statusMap, ValidationDetail } from "@/lib/definitions/api"
import { intlFormatDistance } from "date-fns"
import SeverityLevelChip from "@/components/SeverityLevelChip.vue"
import { filesize } from "filesize"

const p = defineProps<{
  validation: ValidationDetail
}>()

let sushiAttrs: {
  attr:
    | "url"
    | "requested_cop_version"
    | "api_endpoint"
    | "requested_report_code"
    | "requested_begin_date"
    | "requested_end_date"
    | "requested_extra_attributes"
  name: string
}[] = [
  { attr: "url", name: "API URL" },
  { attr: "requested_cop_version", name: "CoP version" },
  { attr: "api_endpoint", name: "API endpoint" },
]
if (p.validation.api_endpoint === "/reports/[id]") {
  sushiAttrs = sushiAttrs.concat([
    { attr: "requested_report_code", name: "Report" },
    { attr: "requested_begin_date", name: "Begin date" },
    { attr: "requested_end_date", name: "End date" },
    { attr: "requested_extra_attributes", name: "Extra attributes" },
  ])
}

const relCreated = computed(() => {
  if (p.validation && p.validation.created)
    return intlFormatDistance(p.validation.created, Date.now())
  return ""
})

function stringify(obj: string | object | null): string {
  if (typeof obj === "string") {
    return obj
  }
  if (Array.isArray(obj)) {
    return obj.map((o) => o.toString()).join("|")
  }
  if (obj !== null) {
    return obj.toString()
  }
  return ""
}
</script>
