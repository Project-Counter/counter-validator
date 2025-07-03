<template>
  <table class="overview">
    <tbody>
      <tr>
        <th>CoP version</th>
        <td>{{ validation.cop_version }}</td>
      </tr>
      <tr>
        <th>Report</th>
        <td>{{ validation.report_code }}</td>
      </tr>
      <tr v-if="validation.result_data">
        <th>Date range</th>
        <td>
          {{ validation.result_data.reportinfo.begin_date }} &ndash;
          {{ validation.result_data.reportinfo.end_date }}
        </td>
      </tr>
      <tr v-if="validation.result_data">
        <th>Institution name</th>
        <td>{{ validation.result_data.reportinfo.institution_name }}</td>
      </tr>
      <tr v-if="validation.result_data">
        <th>Created by</th>
        <td>{{ validation.result_data.reportinfo.created_by }}</td>
      </tr>
      <tr v-if="validation.result_data">
        <th>Created</th>
        <td>{{ validation.result_data.reportinfo.created }}</td>
      </tr>
    </tbody>
  </table>
</template>
<script setup lang="ts">
import { ValidationDetail } from "@/lib/definitions/api"

defineProps<{
  validation: ValidationDetail
}>()
</script>
