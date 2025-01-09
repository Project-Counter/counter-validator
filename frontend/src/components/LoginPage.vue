<template>
  <v-sheet
    class="mx-auto pa-4"
    rounded
    width="480"
  >
    <h2 class="mb-3">{{ page }}</h2>
    <v-form
      validate-on="invalid-input"
      @submit.prevent="doLogin"
    >
      <v-row
        v-if="page == Page.Signup"
        v-bind="rowAttrs"
      >
        <v-col v-bind="colAttrs">
          <v-text-field
            v-model="firstName"
            counter
            label="First name"
            :maxlength="150"
            :rules="[rules.required]"
            variant="outlined"
          />
        </v-col>
        <v-col v-bind="colAttrs">
          <v-text-field
            v-model="lastName"
            counter
            label="Last name"
            :maxlength="150"
            :rules="[rules.required]"
            variant="outlined"
          />
        </v-col>
      </v-row>

      <v-row v-bind="rowAttrs">
        <v-col v-bind="colAttrs">
          <v-text-field
            v-model="email"
            :autofocus="true"
            class="mt-3"
            counter
            label="Email address"
            :maxlength="254"
            prepend-inner-icon="mdi-email"
            :rules="[rules.required, rules.email]"
            variant="outlined"
            @keyup.enter.stop="doLogin"
          />
        </v-col>
      </v-row>

      <v-row
        v-if="page != Page.Forgotten"
        v-bind="rowAttrs"
      >
        <v-col v-bind="colAttrs">
          <v-text-field
            v-model="password"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            class="mt-3"
            label="Password"
            prepend-inner-icon="mdi-key"
            :rules="[rules.required]"
            :type="showPassword ? 'text' : 'password'"
            variant="outlined"
            @click:append-inner="showPassword = !showPassword"
            @keyup.enter.stop="doLogin"
          />
        </v-col>
      </v-row>

      <v-row v-bind="rowAttrs">
        <v-col v-bind="colAttrs">
          <v-btn
            block
            size="large"
            class="mt-4"
            color="primary"
            :disabled="loading"
            :loading="loading"
            :text="page"
            type="submit"
          />
        </v-col>
      </v-row>

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
    </v-form>
  </v-sheet>
</template>

<script setup lang="ts">
import { login, signup, requestPasswordReset } from "@/lib/http/auth"
import * as rules from "@/lib/formRules"
import { LoginSubPage as Page } from "@/lib/login"

const emit = defineEmits(["login"])

const props = defineProps<{
  initialPage?: Page
}>()

const page = ref(props.initialPage || Page.Login)
const email = ref("")
const password = ref("")
const showPassword = ref(false)
const loading = ref(false)
const firstName = ref("")
const lastName = ref("")

async function doLogin() {
  loading.value = true
  try {
    switch (page.value) {
      case Page.Login:
        await login(email.value, password.value)
        emit("login")
        break
      case Page.Signup:
        await signup(email.value, password.value, password.value, {
          first_name: firstName.value,
          last_name: lastName.value,
        })
        emit("login")
        break
      case Page.Forgotten:
        await requestPasswordReset(email.value)
        break
    }
  } finally {
    loading.value = false
  }
}

// styling
const rowAttrs = { class: "py-0 mt-0" }
const colAttrs = { class: "py-0" }
</script>
