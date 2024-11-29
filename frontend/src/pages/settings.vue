<template>
  <v-sheet
    class="mx-auto"
    :max-width="960"
  >
    <h2>Settings</h2>

    <h3 class="mt-10">Account</h3>
    <p class="text-caption text-medium-emphasis mb-3">Some info about you</p>

    <user-form />
    <change-password />

    <h3 class="mt-10">API keys</h3>
    <p class="text-caption text-medium-emphasis mb-3">
      Manage tokens for computer access to the Validation Tool
    </p>

    <api-key-table />
  </v-sheet>
</template>

<script setup lang="ts"></script>
