<template>
  <v-tooltip v-if="user">
    <template #activator="{ props }">
      <span
        v-bind="props"
        class="cursor-pointer"
        @click="copyEmail"
      >
        {{
          user.first_name || user.last_name ? `${user.first_name} ${user.last_name}` : user.email
        }}
      </span>
    </template>
    <span>{{ user.email }}</span>
  </v-tooltip>
</template>

<script setup lang="ts">
import { User } from "@/lib/definitions/api"
import { useAppStore } from "@/stores/app"

const props = defineProps<{ user?: User }>()
const store = useAppStore()

function copyEmail() {
  if (props.user?.email) {
    navigator.clipboard.writeText(props.user.email)
    store.displayNotification({
      message: "Email copied to clipboard",
      type: "success",
    })
  }
}
</script>
