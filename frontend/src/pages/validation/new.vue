<template>
  <v-sheet
    class="mx-auto"
    :max-width="960"
  >
    <v-tabs
      v-model="tab"
      align-tabs="center"
      color="primary"
      fixed-tabs
    >
      <v-tab
        prepend-icon="mdi-file"
        value="file"
      >
        File
      </v-tab>

      <v-tab
        prepend-icon="mdi-lan-connect"
        value="sushi"
      >
        COUNTER API (SUSHI)
      </v-tab>
    </v-tabs>

    <v-tabs-window
      v-model="tab"
      class="mt-5 pa-1"
    >
      <v-tabs-window-item value="file">
        <new-file-validation />
      </v-tabs-window-item>
      <v-tabs-window-item value="sushi">
        <new-sushi-validation />
      </v-tabs-window-item>
    </v-tabs-window>
  </v-sheet>
</template>

<script setup lang="ts">
const tab = ref(null)
</script>
