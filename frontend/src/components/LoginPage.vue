<template>
  <v-sheet
    class="mx-auto pa-4"
    rounded
    width="480"
  >
    <h2 class="mb-3">{{ page }}</h2>

    <LoginDialog v-if="page == Page.Login" />
    <SignupDialog v-else-if="page == Page.Signup" />
    <RequestPasswordResetDialog v-else-if="page == Page.Forgotten" />

    <v-row class="d-flex justify-space-between pt-8">
      <v-col
        v-if="page != Page.Login"
        cols="auto"
      >
        <v-btn
          color="primary"
          :text="Page.Login"
          variant="outlined"
          @click="page = Page.Login"
        />
      </v-col>
      <v-col
        v-if="page != Page.Signup"
        cols="auto"
      >
        <v-btn
          color="primary"
          :text="Page.Signup"
          variant="outlined"
          @click="page = Page.Signup"
        />
      </v-col>
      <v-col
        v-if="page != Page.Forgotten"
        cols="auto"
      >
        <v-btn
          color="primary"
          :text="Page.Forgotten"
          variant="outlined"
          @click="page = Page.Forgotten"
        />
      </v-col>
    </v-row>
  </v-sheet>
</template>

<script setup lang="ts">
import { LoginSubPage as Page } from "@/lib/login"

const props = defineProps<{
  initialPage?: Page
}>()

const page = ref(props.initialPage || Page.Login)
</script>
