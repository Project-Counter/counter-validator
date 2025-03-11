<template>
  <v-card max-width="600">
    <v-card-title>
      <v-checkbox
        v-model="autorenew"
        label="Auto-renew"
        class="float-end"
        density="compact"
        hide-details
      ></v-checkbox>
      Validation queue
    </v-card-title>
    <v-card-text>
      <v-row class="pa-2">
        <v-col
          cols="12"
          sm="4"
        >
          <div class="font-weight-medium">Running Validations</div>
          <v-chip :color="runningNumberColor">{{ runningNumber }}</v-chip>
        </v-col>
        <v-col
          cols="12"
          sm="4"
        >
          <div class="font-weight-medium">Validations in Queue</div>
          <v-chip :color="queueLengthColor">{{ queueLength }}</v-chip>
        </v-col>
        <v-col
          cols="12"
          sm="4"
        >
          <div class="font-weight-medium">Number of Workers</div>
          <v-chip :color="workerNumberColor">{{ workerNumber }}</v-chip>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { getQueueInfo } from "@/lib/http/validation"

const queueLength = ref<number>(0)
const runningNumber = ref<number>(0)
const workerNumber = ref<number>(0)

const loading = ref(false)
const autorenew = ref(false)
const refreshTimeout = 2000
let autorenewTimeout: number | null = null

async function load() {
  loading.value = true
  try {
    const out = await getQueueInfo()
    queueLength.value = out.queued
    runningNumber.value = out.running
    workerNumber.value = out.workers
  } finally {
    loading.value = false
  }
  if (autorenew.value) {
    autorenewTimeout = setTimeout(load, refreshTimeout)
  }
}

watch(autorenew, () => {
  if (autorenew.value && !loading.value) {
    load()
  } else if (autorenewTimeout) {
    clearTimeout(autorenewTimeout)
    autorenewTimeout = null
  }
})

const queueLengthColor = computed(() => {
  if (queueLength.value === 0) {
    return "success"
  } else if (queueLength.value <= workerNumber.value) {
    return "info"
  } else if (queueLength.value <= 2 * workerNumber.value) {
    return "warning"
  }
  return "error"
})

const workerNumberColor = computed(() => {
  if (workerNumber.value === 0) {
    return "error"
  }
  return "info"
})

const runningNumberColor = computed(() => {
  return "success"
})

onMounted(load)
onUnmounted(() => {
  if (autorenewTimeout) clearTimeout(autorenewTimeout)
})
</script>

<style scoped></style>
