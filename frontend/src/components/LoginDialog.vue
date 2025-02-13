<template>
  <v-form
    validate-on="invalid-input"
    @submit.prevent="doLogin"
  >
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
          :rules="[rules.required]"
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
          variant="flat"
          size="large"
          class="mt-4"
          color="primary"
          :disabled="loading"
          :loading="loading"
          type="submit"
        >
          Login
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script setup lang="ts">
import { login } from "@/lib/http/auth"
import * as rules from "@/lib/formRules"
import { HttpStatusError } from "@/lib/http/util"
import { useAppStore } from "@/stores/app"

const emit = defineEmits(["login"])

const store = useAppStore()

const email = ref("")
const password = ref("")
const showPassword = ref(false)
const loading = ref(false)

const emailMessage = ref<string | null>(null)
const passwordMessage = ref<string | null>(null)

async function doLogin() {
  loading.value = true
  try {
    await login(email.value, password.value)
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
      if (data.non_field_errors) {
        store.displayNotification({ message: data.non_field_errors[0], type: "error" })
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
