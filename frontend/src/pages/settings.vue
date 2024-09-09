<template>
  <v-sheet
    class="mx-auto"
    :max-width="960"
  >
    <h2>Settings</h2>

    <h3 class="mt-6">
      Looks
    </h3>
    <p class="text-caption text-medium-emphasis mb-3">
      Theme settings saved only in this browser
    </p>
    <v-switch
      v-model="darkTheme"
      class="my-n3"
      color="primary"
      hide-details
      label="Dark theme"
    />

    <h3 class="mt-10">
      Account
    </h3>
    <p class="text-caption text-medium-emphasis mb-3">
      Some info about you
    </p>

    <user-form />
    <change-password />

    <h3 class="mt-10">
      API keys
    </h3>
    <p class="text-caption text-medium-emphasis mb-3">
      Manage tokens for computer access to the Validation Tool
    </p>

    <api-key-table />
  </v-sheet>
</template>

<script setup lang="ts">
import { useTheme } from "vuetify"

// Theme
const theme = useTheme()
const darkTheme = computed({
	get: () => theme.global.current.value.dark,
	set: v => theme.global.name.value = !v ? "light" : "dark",
})

</script>
