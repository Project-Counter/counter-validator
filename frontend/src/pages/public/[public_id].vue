<template>
  <ValidationDetailWidget
    v-if="validation"
    :validation="validation"
    public-view
  />
  <v-alert
    v-else-if="validationNotFound"
    type="error"
  >
    Validation not found. It may have been removed or is no longer published.
  </v-alert>
</template>

<script setup lang="ts">
import { ValidationDetail } from "@/lib/definitions/api"
import { getPublicValidationDetail } from "@/lib/http/validation"
import { HttpStatusError } from "@/lib/http/util"

const validation = ref<ValidationDetail>()
const route = useRoute()
const validationNotFound = ref<boolean>(false)

async function load() {
  if ("public_id" in route.params) {
    // check needed for TS to narrow down the type
    try {
      validation.value = await getPublicValidationDetail(route.params.public_id)
    } catch (e) {
      if (e instanceof HttpStatusError && e.res?.status === 404) {
        validationNotFound.value = true
      } else {
        throw e
      }
    }
  }
}

onMounted(load)
</script>

<style scoped lang="scss"></style>

<route>
meta:
  requiresAuth: false
</route>
