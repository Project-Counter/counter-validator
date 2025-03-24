<template>
  <ValidationDetailWidget
    v-if="validation"
    :validation="validation"
  />
  <v-alert
    v-else-if="validationNotFound"
    type="error"
    class="ma-8"
  >
    <p>
      This validation does not exist. It may have been removed - either by the user or through
      expiration.
    </p>
  </v-alert>
</template>

<script setup lang="ts">
import { Status, ValidationDetail } from "@/lib/definitions/api"
import { getValidationDetail } from "@/lib/http/validation"
import { HttpStatusError } from "@/lib/http/util"

const validation = ref<ValidationDetail>()
const route = useRoute()
const validationNotFound = ref<boolean>(false)
const timeoutHandle = ref<number | null>(null)

async function load() {
  if ("id" in route.params) {
    // check needed for TS to narrow down the type
    try {
      validation.value = await getValidationDetail(route.params.id)
    } catch (e) {
      if (e instanceof HttpStatusError && e.res?.status === 404) {
        validationNotFound.value = true
      } else {
        throw e
      }
    }
    if (
      validation.value?.status === Status.RUNNING ||
      validation.value?.status === Status.WAITING
    ) {
      timeoutHandle.value = setTimeout(load, 2000)
    }
  }
}

onMounted(load)

onUnmounted(() => {
  if (timeoutHandle.value) {
    clearTimeout(timeoutHandle.value)
    timeoutHandle.value = null
  }
})
</script>

<style scoped lang="scss"></style>
