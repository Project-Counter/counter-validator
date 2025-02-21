<template>
  <v-app>
    <v-app-bar
      color="white"
      height="128"
    >
      <a
        href="https://www.countermetrics.org/"
        target="_blank"
        class="ml-1300 pl-4 py-4 hidden-sm-and-down"
      >
        <img
          src="/counter_logo_secondary.png"
          alt="COUNTER logo"
          height="28"
        />
      </a>
      <v-spacer></v-spacer>
      <h1 class="text-h4 text-primary font-weight-bold mr-1300 pr-4">
        <router-link
          to="/"
          class="text-decoration-none raleway"
          >COUNTER Validation Tool</router-link
        >
      </h1>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view v-if="store.user || route.meta.requiresAuth === false" />

        <v-alert
          v-else
          type="warning"
        >
          <template #title>Log in required</template>
          <template #text>
            <p>You need to log in to access this page.</p>
            <p>
              <router-link to="/login">Log in</router-link>
            </p>
          </template>
        </v-alert>
      </v-container>
    </v-main>
    <v-footer
      app
      border
      color="secondary"
      class="pt-2 pt-md-8 pb-2 pb-md-16 px-2 px-md-8"
    >
      <v-container max-width="1300px">
        <v-row>
          <v-col cols="auto">&copy; {{ new Date().getFullYear() }} COUNTER Metrics Limited</v-col>
          <v-spacer></v-spacer>
          <v-col
            v-if="store.user"
            cols="auto"
          >
            Logged in as:
            <router-link
              to="/settings"
              class="font-weight-light text-white"
              >{{ store.user.email }}</router-link
            >
          </v-col>
          <v-spacer v-if="store.user"></v-spacer>
          <v-col cols="auto">
            <a
              href="https://www.countermetrics.org/terms-and-conditions/"
              target="_blank"
              class="text-white"
              >Terms &amp; Conditions</a
            >
          </v-col>
          <v-col cols="auto">
            <a
              href="https://www.countermetrics.org/privacy-data-protection/"
              target="_blank"
              class="text-white"
              >Privacy &amp; Data Protection</a
            >
          </v-col>
          <v-col cols="auto">
            <a
              href="https://www.countermetrics.org/accessibility/"
              target="_blank"
              class="text-white"
              >Accessibility</a
            >
          </v-col>
        </v-row>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import { useAppStore } from "@/stores/app"

const store = useAppStore()

const route = useRoute()
</script>
