<template>
  <v-form
    v-model="form"
    class="d-inline"
    @submit.prevent="save"
  >
    <v-row class="mb-0">
      <v-col
        cols="12"
        md="6"
      >
        <v-text-field
          v-model="user.first_name"
          counter
          label="First name"
          :maxlength="150"
        />
      </v-col>
      <v-col
        cols="12"
        md="6"
      >
        <v-text-field
          v-model="user.last_name"
          counter
          label="Last name"
          :maxlength="150"
        />
      </v-col>
    </v-row>
    <v-row class="mt-0">
      <v-col
        cols="12"
        md="6"
      >
        <v-text-field
          v-model="user.email"
          class="mb-2"
          counter
          label="Email address"
          :maxlength="254"
          :rules="[rules.required, rules.email]"
        />
      </v-col>

      <!-- Email verification status -->
      <v-col
        v-if="store.userVerified"
        class="d-flex align-center mb-4"
        cols="12"
        md="6"
      >
        <v-icon color="success">mdi-check</v-icon>
        <span class="ml-2">Email verified</span>
      </v-col>
      <v-col
        v-else
        class="d-flex align-center mb-4 justify-space-between"
        cols="12"
        md="6"
      >
        <span>
          <v-icon color="error">mdi-alert</v-icon>
          <span class="ml-2">Email not verified</span>
        </span>
        <v-btn
          color="primary"
          class="ml-6"
          variant="tonal"
          @click="sendVerificationEmail"
        >
          <v-icon class="pr-2">mdi-send</v-icon>
          Resend verification email
        </v-btn>
      </v-col>
    </v-row>

    <v-btn
      :disabled="!form || saved"
      :loading="loading"
      text="Save"
      type="submit"
    />
  </v-form>
</template>

<script setup lang="ts">
import * as rules from "@/lib/formRules"
import { User } from "@/lib/definitions/api"
import { updateAccount, resendVerificationEmail } from "@/lib/http/auth"
import { useAppStore } from "@/stores/app"

const store = useAppStore()

const form = ref(false)
const loading = ref(false)
const user = ref<User>(
  store.user ? { ...store.user } : { first_name: "", last_name: "", email: "" },
)
const saved = computed(() => {
  if (!store.user) return false
  for (const key of Object.keys(user.value) as Array<keyof User>) {
    if (user.value[key] !== store.user[key]) return false
  }
  return true
})
async function save() {
  loading.value = true
  user.value.first_name = user.value.first_name.replace(/\s+/g, " ")
  user.value.last_name = user.value.last_name.replace(/\s+/g, " ")
  await updateAccount(user.value)
  if (store.user) user.value = { ...store.user }
  loading.value = false
}

async function sendVerificationEmail() {
  await resendVerificationEmail(user.value.email)
  store.displayNotification({
    message: "Verification email sent",
    type: "success",
  })
}
</script>
