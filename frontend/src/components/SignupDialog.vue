<template>
  <v-form
    v-model="valid"
    validate-on="input"
    @submit.prevent="doSignup"
  >
    <v-row v-bind="rowAttrs">
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
          :error-messages="emailMessage"
        />
      </v-col>
    </v-row>

    <v-row v-bind="rowAttrs">
      <v-col v-bind="colAttrs">
        <v-text-field
          v-model="password"
          :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
          class="mt-3"
          label="Password"
          prepend-inner-icon="mdi-key"
          :rules="[rules.required, rules.password]"
          :type="showPassword ? 'text' : 'password'"
          variant="outlined"
          :error-messages="passwordMessage"
          @click:append-inner="showPassword = !showPassword"
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
          :disabled="loading || !valid"
          :loading="loading"
          text="Create account"
          type="submit"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script setup lang="ts">
import { signup } from "@/lib/http/auth"
import * as rules from "@/lib/formRules"
import { HttpStatusError } from "@/lib/http/util"

const emit = defineEmits(["login"])

const valid = ref(false)
const email = ref("")
const password = ref("")
const showPassword = ref(false)
const loading = ref(false)
const firstName = ref("")
const lastName = ref("")

// error messages
const emailMessage = ref<string | null>(null)
const passwordMessage = ref<string | null>(null)

watch(email, () => {
  emailMessage.value = null
})

watch(password, () => {
  passwordMessage.value = null
})

// methods
async function doSignup() {
  loading.value = true
  try {
    await signup(email.value, password.value, password.value, {
      first_name: firstName.value,
      last_name: lastName.value,
    })
    emit("login")
  } catch (error) {
    if (error instanceof HttpStatusError && error.res.status === 400) {
      const data = await error.res.json()
      if (data.email) {
        emailMessage.value = data.email[0]
      }
      if (data.password) {
        passwordMessage.value = data.password[0]
      }
    }
  } finally {
    loading.value = false
  }
}

// styling
const rowAttrs = { class: "py-0 mt-0" }
const colAttrs = { class: "pt-0" }
</script>

<style scoped></style>
