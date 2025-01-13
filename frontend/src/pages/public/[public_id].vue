<template>
  <ValidationDetailWidget
    v-if="validation"
    :validation="validation"
    public-view
  />
</template>

<script setup lang="ts">
import { ValidationDetail } from "@/lib/definitions/api"
import { getPublicValidationDetail } from "@/lib/http/validation"

const validation = ref<ValidationDetail>()
const route = useRoute()

async function load() {
  if ("public_id" in route.params) {
    // check needed for TS to narrow down the type
    validation.value = await getPublicValidationDetail(route.params.public_id)
  }
}

onMounted(load)
</script>

<style scoped lang="scss"></style>

<route>
meta:
  requiresAuth: false
</route>
