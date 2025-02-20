<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>COUNTER Validation Tool</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <p>Version {{ version.server }}</p>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <p>Copyright &copy; 2024&ndash;{{ currentYear }} COUNTER Metrics Limited</p>
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
