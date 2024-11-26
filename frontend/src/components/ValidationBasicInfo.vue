<template>
  <table class="overview">
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
    class="overview"
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
              <th>{{ key }}</th>
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
        <td>{{ validation[attr.attr] }}</td>
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
    | "requested_cop_version"
    | "api_endpoint"
    | "requested_report_code"
    | "requested_begin_date"
    | "requested_end_date"
    | "requested_extra_attributes"
  name: string
}[] = [
  { attr: "requested_cop_version", name: "CoP version" },
  { attr: "api_endpoint", name: "API endpoint" },
]
if (p.validation.api_endpoint === "reports") {
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
</script>
