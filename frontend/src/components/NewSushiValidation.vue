<template>
  <v-stepper :items="['Server selection', 'Report selection', 'Validation']">
    <template #item.1>
      <h2 class="mb-3">
        Server
      </h2>
      <v-autocomplete
        hint="Type to search in the COUNTER Registry"
        label="Search in platforms"
        persistent-hint
        prepend-inner-icon="mdi-magnify"
      />
      <div class="my-3">
        <v-divider>or enter manually</v-divider>
      </div>
      <v-row>
        <v-col
          cols="12"
          md="8"
        >
          <v-text-field
            hide-details
            label="URL"
          />
        </v-col>
        <v-col
          cols="12"
          md="4"
        >
          <v-text-field
            hint="Fill only if server requires it"
            label="Platform"
          />
        </v-col>
      </v-row>

      <h2 class="mt-4 mb-3">
        Credentials
      </h2>
      <v-row>
        <v-col
          cols="12"
          md="4"
        >
          <v-text-field
            hide-details
            label="Customer ID"
          />
        </v-col>
        <v-col
          cols="12"
          md="4"
        >
          <v-text-field
            hide-details
            label="Requestor ID"
          />
        </v-col>
        <v-col
          cols="12"
          md="4"
        >
          <v-text-field
            hide-details
            label="API key"
          />
        </v-col>
      </v-row>

      <div class="text-end my-5 ">
        <v-btn
          class="ma-2"
          prepend-icon="mdi-help-circle-outline"
        >
          Get status
        </v-btn>
        <v-btn
          class="ma-2"
          prepend-icon="mdi-account-multiple"
        >
          Get members
        </v-btn>
      </div>
    </template>
  </v-stepper>
</template>

<script setup lang="ts">
</script>
