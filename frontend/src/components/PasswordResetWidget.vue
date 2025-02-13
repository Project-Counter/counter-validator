<template>
  <v-card
    max-width="640px"
    class="mx-auto"
    variant="outlined"
    border="sm"
  >
    <v-card-title>{{
      invitation ? "Accept invitation and create account" : "Reset your password"
    }}</v-card-title>

    <v-card-text>
      <p class="my-4">
        Please choose a {{ invitation ? "" : "new" }} password for your account. Your password must
        be at least 8 characters long and contain at least one letter and one number.
      </p>
      <v-form
        v-if="hasParams"
        v-model="valid"
        @submit.prevent="submit"
      >
        <v-text-field
          v-model="password"
          label="Password"
          type="password"
          required
          :rules="[rules.required, rules.password]"
          :error-messages="passwordMessage"
          class="mb-4"
        />
        <v-btn
          color="primary"
          type="submit"
          :disabled="!valid"
          >{{ invitation ? "Create account" : "Reset password" }}</v-btn
        >
      </v-form>
      <v-alert
        v-else
        type="error"
        variant="outlined"
      >
        <h3>{{ invitation ? "Invalid invitation link" : "Invalid reset link" }}</h3>
        <p v-if="invitation">
          Unfortunately this invitation link is invalid. It may have been corrupted during
          transmission, or you may have copied only part of it. Please check the link and try again.
          Alternatively, you can request a new invitation.
        </p>
        <p v-else>
          Unfortunately this reset link is invalid. It may have been corrupted during transmission,
          or you may have copied only part of it. Please check the link and try again.
          Alternatively, you can request a new reset link.
        </p>
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { doPasswordReset } from "@/lib/http/auth"
import { useAppStore } from "@/stores/app"
import { HttpStatusError } from "@/lib/http/util"
import * as rules from "@/lib/formRules"

const props = withDefaults(
  defineProps<{
    invitation?: boolean
  }>(),
  {
    invitation: false,
  },
)

const store = useAppStore()
const route = useRoute()
const router = useRouter()

const uid = ref<string>(
  (Array.isArray(route.query.uid) ? route.query.uid[0] : route.query.uid) || "",
)
const token = ref<string>(
  (Array.isArray(route.query.token) ? route.query.token[0] : route.query.token) || "",
)
const hasParams = computed(() => uid.value && token.value)

const password = ref<string>("")
const passwordMessage = ref<string | null>(null)
const valid = ref(false)

watch(password, () => {
  passwordMessage.value = null
})

const resetInvalidText =
  "The reset token is no longer valid. It may have expired or has already been used. " +
  "Please request a new password reset link."
const invitationInvalidText =
  "The invitation link is no longer valid. It may have expired or has already been used. " +
  "Please request a new invitation."

async function submit() {
  try {
    let out = await doPasswordReset(uid.value, token.value, password.value, password.value)
    store.displayNotification({ type: "success", message: out.detail })
  } catch (err) {
    if (err instanceof HttpStatusError && err.res.status === 400) {
      const data = await err.res.json()
      if (data?.token) {
        store.displayNotification({
          type: "error",
          message: props.invitation ? invitationInvalidText : resetInvalidText,
        })
      } else if (data?.uid) {
        store.displayNotification({ type: "error", message: data.uid })
      } else if (data?.detail) {
        store.displayNotification({ type: "error", message: data.detail })
      } else if (data?.new_password1 || data?.new_password2) {
        passwordMessage.value = data.new_password1 || data.new_password2
      } else {
        store.displayNotification({
          type: "error",
          message: "An error occurred. Please try again.",
        })
      }
    } else {
      store.displayNotification({ type: "error", message: "An error occurred. Please try again." })
    }
    return
  }
  router.push("/login")
}
</script>

<style scoped></style>
