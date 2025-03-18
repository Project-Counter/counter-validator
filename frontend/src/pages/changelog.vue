<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Changelog</h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <ChangelogWidget />
      </v-col>
    </v-row>
  </v-container>
</template>

<route>
meta:
  requiresAuth: false
  layout: "public"
</route>
