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
        <th>Expiration date</th>
        <td>{{ validation?.expiration_date }} ({{ relExpirationDate }})</td>
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
      <tr v-if="!publicView">
        <th>Visibility</th>
        <td>
          <v-icon
            color="subdued"
            size="small"
            class="pb-1"
            >mdi-{{ publicId ? "eye" : "eye-off" }}</v-icon
          >
          {{ publicId ? "Public" : "Private" }}

          <v-tooltip
            v-if="publicId"
            bottom
            max-width="600px"
          >
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                size="x-small"
                class="ml-2 mb-1"
                color="error"
                @click="unpublish"
              >
                Hide
              </v-btn>
            </template>
            Hiding the validation result will invalidate the unique link which allows read-only
            access to the validation result. Hiding and re-sharing the result will generate a new
            unique link.
          </v-tooltip>

          <v-tooltip
            v-else
            bottom
            max-width="600px"
          >
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                size="x-small"
                class="ml-2 mb-1"
                color="success"
                @click="publish"
              >
                Share
              </v-btn>
            </template>
            Sharing a validation result will create a unique link which will add read-only access to
            the validation result to anyone with the link. Shared result can be hidden again at any
            time. Shared validations do not show the used COUNTER API credentials.
          </v-tooltip>

          <router-link
            v-if="publicId"
            :to="`/public/${publicId}`"
            class="ml-4"
            >Public link</router-link
          >
        </td>
      </tr>
      <tr>
        <th>Note</th>
        <td>{{ validation.user_note }}</td>
      </tr>
    </tbody>
  </table>

  <h3
    v-if="validation.requested_cop_version"
    class="text-h6 mt-4 mb-2"
  >
    Requested COUNTER API parameters
  </h3>
  <table
    v-if="validation.requested_cop_version"
    class="overview ml-4"
  >
    <tbody>
      <tr>
        <th>Credentials</th>
        <td>
          <table
            v-if="validation.credentials"
            class="dense"
          >
            <tr
              v-for="(value, key) in validation.credentials"
              :key="key"
            >
              <th class="font-weight-regular">{{ key }}</th>
              <td>{{ value }}</td>
            </tr>
          </table>
          <!-- we don't have credentials for public view -->
          <span v-else>-</span>
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
import { filesize } from "filesize"
import { publishValidation, unpublishValidation } from "@/lib/http/validation"

const p = withDefaults(
  defineProps<{
    validation: ValidationDetail
    publicView?: boolean
  }>(),
  {
    publicView: false,
  },
)

const publicId = ref(p.validation.public_id)

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

// relative time

const relCreated = computed(() => {
  if (p.validation && p.validation.created)
    return intlFormatDistance(p.validation.created, Date.now())
  return ""
})

const relExpirationDate = computed(() => {
  if (p.validation && p.validation.expiration_date)
    return intlFormatDistance(p.validation.expiration_date, Date.now())
  return ""
})

// stringifying

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

// publishing/unpublishing

async function publish() {
  const res = await publishValidation(p.validation.id)
  publicId.value = res.public_id
}

async function unpublish() {
  const res = await unpublishValidation(p.validation.id)
  publicId.value = res.public_id
}
</script>
