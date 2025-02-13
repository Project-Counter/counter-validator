<template>
  <v-form
    v-model="valid"
    validate-on="input"
    @submit.prevent="doPasswordReset"
  >
    <v-row v-bind="rowAttrs">
      <v-col class="mb-4">
        Please enter the email address associated with your account. We will send you an email with
        a link to reset your password.
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
          text="Reset password"
          type="submit"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script setup lang="ts">
import { requestPasswordReset } from "@/lib/http/auth"
import * as rules from "@/lib/formRules"
import { useAppStore } from "@/stores/app"

const emit = defineEmits(["password-reset"])

const store = useAppStore()

const email = ref("")
const loading = ref(false)
const valid = ref(false)

async function doPasswordReset() {
  loading.value = true
  try {
    await requestPasswordReset(email.value)
    emit("password-reset")
    store.displayNotification({
      message: "Password reset email sent. Please check your inbox.",
      type: "success",
    })
  } finally {
    loading.value = false
  }
}

// styling
const rowAttrs = { class: "py-0 mt-0" }
const colAttrs = { class: "pt-0" }
</script>

<style scoped></style>
