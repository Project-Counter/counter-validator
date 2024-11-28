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
      <tr>
        <th>Created by</th>
        <td>{{ validation.result_data.header.created_by }}</td>
      </tr>
      <tr>
        <th>Institution name</th>
        <td>{{ validation.result_data.header.institution_name }}</td>
      </tr>
      <tr>
        <th>Date range</th>
        <td>
          {{ validation.result_data.header.begin_date }} &ndash;
          {{ validation.result_data.header.end_date }}
        </td>
      </tr>
      <tr>
        <th>Created</th>
        <td>{{ validation.result_data.header.created }}</td>
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
