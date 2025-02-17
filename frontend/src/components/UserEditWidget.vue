<template>
  <v-card>
    <v-card-title class="mx-4 mt-4">{{ user ? "Edit user" : "Create user" }}</v-card-title>
    <v-card-text>
      <v-form v-model="valid">
        <v-container
          fluid
          class="pa-0"
        >
          <v-row>
            <v-col
              cols="12"
              md="3"
              class="pb-0"
            >
              <v-text-field
                v-model="firstName"
                label="First name"
                required
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col
              cols="12"
              md="3"
              class="pb-0"
            >
              <v-text-field
                v-model="lastName"
                label="Last name"
                required
                :rules="[requiredRule]"
              />
            </v-col>
            <v-col
              cols="12"
              md="6"
              class="pb-0"
            >
              <v-text-field
                v-model="email"
                label="Email"
                required
                append-inner-icon="mdi-email"
                :rules="[requiredRule, emailRule]"
                :error-messages="emailErrorMessages"
                persistent-hint
              />
            </v-col>
            <v-col
              cols="6"
              md="auto"
              class="pt-0 ml-2"
            >
              <v-tooltip
                max-width="600px"
                location="bottom"
              >
                <template #activator="{ props }">
                  <v-checkbox
                    v-bind="props"
                    v-model="isValidatorAdmin"
                    label="Is admin"
                    hide-details
                    density="compact"
                    :disabled="user?.id === store.user?.id"
                  />
                </template>
                Validator admins can manage other users and have access to all validations.
              </v-tooltip>
            </v-col>
            <v-col
              cols="6"
              md="auto"
              class="pt-0"
            >
              <v-tooltip
                location="bottom"
                max-width="600px"
              >
                <template #activator="{ props }">
                  <v-checkbox
                    v-bind="props"
                    v-model="isActive"
                    label="Is active"
                    hide-details
                    density="compact"
                    :disabled="user?.id === store.user?.id"
                  />
                </template>
                Inactive users cannot log in - use for temporary account suspension.
              </v-tooltip>
            </v-col>
          </v-row>
        </v-container>
      </v-form>
    </v-card-text>

    <v-card-actions class="ma-4">
      <!-- buttons -->
      <v-btn
        color="subdued"
        variant="tonal"
        @click="emit('cancel')"
      >
        Cancel
      </v-btn>

      <v-btn
        v-if="!user"
        variant="tonal"
        :disabled="!valid"
        color="secondary"
        @click="saveUser(true)"
        >Create & invite</v-btn
      >

      <v-btn
        color="primary"
        variant="elevated"
        :disabled="!valid"
        @click="saveUser()"
      >
        {{ user ? "Save" : "Create" }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { createUser, sendInvitationEmail, updateUser } from "@/lib/http/users"
import { User } from "@/lib/definitions/api"
import { HttpStatusError } from "@/lib/http/util"
import { useAppStore } from "@/stores/app"

const props = defineProps<{
  user?: User
}>()

const firstName = ref(props.user?.first_name || "")
const lastName = ref(props.user?.last_name || "")
const email = ref(props.user?.email || "")
const isValidatorAdmin = ref(props.user?.is_validator_admin || false)
const isActive = ref(props.user?.is_active || true)
const valid = ref(false)

const store = useAppStore()

// hints
const emailErrorMessages = ref<string[]>([])

async function saveUser(invite: boolean = false) {
  const userData = {
    first_name: firstName.value,
    last_name: lastName.value,
    email: email.value,
    is_validator_admin: isValidatorAdmin.value,
    is_active: isActive.value,
  }
  try {
    if (props.user) {
      // Update user
      const user = await updateUser({ id: props.user.id, ...userData })
      emit("userUpdated", user)
    } else {
      // Create user
      const user = await createUser(userData)
      if (invite) {
        await sendInvitationEmail(user)
      }
      emit("userCreated", { user, invite })
    }
  } catch (err) {
    if (err instanceof HttpStatusError && err?.res?.status === 400) {
      // Validation error
      const data = await err.res.json()
      if (data.email) {
        emailErrorMessages.value = data.email
      }
    }
  }
}

watch([email], () => {
  // clear email error messages on email change
  emailErrorMessages.value = []
})

const emit = defineEmits(["userCreated", "userUpdated", "cancel"])

const requiredRule = (v: string) => !!v || "This field is required"
const emailRule = (v: string) => /.+@.+\..+/.test(v) || "E-mail must be valid"
</script>

<style scoped></style>
