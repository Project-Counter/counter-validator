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
</template>
<script setup lang="ts">
import { statusMap, ValidationDetail } from "@/lib/definitions/api"
import { intlFormatDistance } from "date-fns"
import SeverityLevelChip from "@/components/SeverityLevelChip.vue"
import { filesize } from "filesize"

const p = defineProps<{
  validation: ValidationDetail
}>()

const relCreated = computed(() => {
  if (p.validation && p.validation.created)
    return intlFormatDistance(p.validation.created, Date.now())
  return ""
})
</script>
