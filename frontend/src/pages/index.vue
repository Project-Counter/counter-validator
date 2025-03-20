<template>
  <v-container max-width="1300px">
    <v-row>
      <v-col>
        <p>
          The COUNTER Validation Tool is a web application that allows you to validate your COUNTER
          reports. It is designed to help you ensure that your reports are compliant with the
          <a
            href="https://cop5.projectcounter.org/"
            target="_blank"
            >COUNTER Code of Practice</a
          >.
        </p>
      </v-col>
    </v-row>

    <v-row>
      <v-col
        cols="12"
        md="8"
        xl="6"
        offset-md="2"
        offset-xl="3"
      >
        <v-card
          color="secondary"
          class="mx-auto pa-6 my-8"
        >
          <v-card-title class="text-h4"
            >{{ store.user || !store.isUserRegistrationAllowed ? "Use" : "Register" }} for
            FREE</v-card-title
          >
          <v-card-text>
            <ul class="ms-6 text-body-1">
              <li>Validate Your COUNTER Release 5 and 5.1 JSON Reports</li>
              <li>Validate Your COUNTER Release 5 and 5.1 Tabular Reports</li>
              <li>Release 5 and 5.1 COUNTER API (sushi) Validation</li>
              <li>Fetch Your Old Test Report</li>
              <li>Test Development Environment</li>
              <li>Share Your Validations with Others</li>
              <li>Get On-Screen Error Display and Download Reports</li>
            </ul>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-0 mb-8">
      <v-col
        v-if="store.user"
        class="text-center"
      >
        <v-btn
          color="primary"
          size="x-large"
          rounded
          to="/validation"
          >To my validations</v-btn
        >
      </v-col>
      <v-col
        v-else
        class="text-center"
      >
        <v-btn
          v-if="store.isUserRegistrationAllowed"
          color="primary"
          size="x-large"
          rounded
          style="min-width: 12rem"
          to="/register"
          >Register</v-btn
        >
        <span
          style="width: 2rem"
          class="d-inline-block"
        ></span>
        <v-btn
          color="secondary"
          size="x-large"
          rounded
          style="min-width: 12rem"
          to="/login"
          >Log in</v-btn
        >
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <p>
          The tool is developed and maintained by
          <a href="https://www.countermetrics.org/">COUNTER Metrics Limited</a>, a not-for-profit
          organisation sustained by the global community of members, including libraries, consortia,
          publishers, aggregators, and technology providers.
        </p>

        <p class="mt-8">
          The COUNTER Validation Tool is published as open source and available on

          <a
            href="https://github.com/Project-Counter/counter-validation-tool"
            target="_blank"
            >GitHub</a
          >. There you will find the complete source code and information about how to run your own
          instance of the tool. You can also report issues and contribute to the project there.
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useAppStore } from "@/stores/app"

const store = useAppStore()
</script>

<style scoped></style>

<route>
meta:
  requiresAuth: false
  layout: "public"
</route>
