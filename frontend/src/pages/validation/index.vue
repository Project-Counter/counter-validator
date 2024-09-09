<template>
  <v-card
    color="primary"
    loading
    max-width="330"
    variant="tonal"
  >
    <template #text />
  </v-card>
  <v-data-table
    :headers="headers"
    :items="items"
    :items-per-page="-1"
    :mobile="null"
  >
    <template #item.status="{ value }">
      <!-- <v-progress-circular v-if="value == 2" color="grey" size="18" indeterminate></v-progress-circular> -->
      <v-icon
        v-if="value == 0"
        color="grey"
      >
        mdi-clock
      </v-icon>
      <v-icon
        v-if="value == 1"
        color="grey"
      >
        mdi-run-fast
      </v-icon>
      <v-icon
        v-else-if="value == 2"
        color="success"
      >
        mdi-checkbox-marked
      </v-icon>
      <v-icon
        v-else
        color="error"
      >
        mdi-alert
      </v-icon>
    </template>
    <template #item.detail="{ item }">
      <v-btn
        v-if="item.status == 2"
        icon="mdi-open-in-app"
        :to="item.id + '/'"
        variant="text"
      />
    </template>
    <template #item.id="{ item }">
      <date-tooltip :date="item.created" />
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
const items = ref([])
const headers = [
	{ key: "status", title: "Status", align: "center", width: 1 },
	{ key: "filename", title: "Filename" },
	{ key: "detail", title: "Detail", sortable: false },
	{ key: "id", title: "Time" },
]

async function load() {
	const response = await fetch("/api/validation/")
	items.value = await response.json()
}
// setInterval(load, 500)
load().then()
</script>
