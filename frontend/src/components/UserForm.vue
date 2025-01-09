<template>
  <v-form
    v-model="form"
    class="d-inline"
    @submit.prevent="save"
  >
    <v-row class="mb-1">
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
    <v-text-field
      v-model="user.email"
      class="mb-2"
      counter
      label="Email address"
      :maxlength="254"
      :rules="[rules.required, rules.email]"
    />
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
import { updateUser } from "@/lib/http/auth"
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
  await updateUser(user.value)
  if (store.user) user.value = { ...store.user }
  loading.value = false
}
</script>
