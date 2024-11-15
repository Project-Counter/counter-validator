<template>
  <v-container>
    <v-row>
      <v-col cols="auto">
        <v-btn
          color="primary"
          size="large"
          :to="{ name: '/validation/file' }"
        >
          <v-icon class="me-2"> mdi-file-cog-outline </v-icon>
          Validate a file
        </v-btn>
      </v-col>

      <v-col cols="auto">
        <v-btn
          color="primary"
          size="large"
          :to="{ name: '/validation/sushi' }"
        >
          <v-icon class="me-2">mdi-server-outline</v-icon>
          Validate API
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <Suspense>
          <ValidationTable />
        </Suspense>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
//
</script>
