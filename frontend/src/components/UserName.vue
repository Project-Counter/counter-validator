<template>
  <span v-if="user"
    >{{ user.first_name || user.last_name ? `${user.first_name} ${user.last_name}` : user.email }}
  </span>
  <span v-else>-</span>
</template>

<script setup lang="ts">
import { User } from "@/lib/definitions/api"

defineProps<{ user?: User }>()
</script>
