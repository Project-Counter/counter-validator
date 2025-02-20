<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>COUNTER Validation Tool</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <p>
          <strong>Version {{ version.server }}</strong>
          <span
            v-if="version.upstream"
            class="text-disabled ps-2"
          >
            (upstream version {{ version.upstream }}
            <span v-if="version.upToDate === false">
              <v-icon color="error">mdi-alert</v-icon> not up to date
            </span>
            <span v-else-if="version.upToDate">
              <v-icon color="success">mdi-check</v-icon> up to date</span
            >)
          </span>
        </p>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <p>&copy; {{ currentYear }} COUNTER Metrics Limited</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useVersionStore } from "@/stores/version"

const currentYear = computed(() => new Date().getFullYear())

const version = useVersionStore()

onBeforeMount(() => {
  version.update()
})
</script>

<style scoped></style>

<route>
meta:
  requiresAuth: false
</route>
