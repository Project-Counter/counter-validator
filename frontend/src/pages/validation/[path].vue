<template>
  <v-tabs
    v-model="tab"
    align-tabs="center"
    color="primary"
    fixed-tabs
  >
    <v-tab
      prepend-icon="mdi-magnify"
      value="details"
    >
      Details
    </v-tab>

    <v-tab
      prepend-icon="mdi-receipt-text"
      value="result"
    >
      Validation result
    </v-tab>
  </v-tabs>
  <v-tabs-window
    v-model="tab"
    class="mt-5 pa-1"
  >
    <v-tabs-window-item value="details">
      <h3 class="mb-5">
        Validation info
      </h3>
      <v-row
        v-for="(v, k, n) in info"
        :key="k"
        :class="n % 2 ? 'bg-surface-light' : ''"
      >
        <v-col
          cols="12"
          md="2"
        >
          {{ k }}
        </v-col>
        <v-col
          cols="12"
          md="10"
        >
          {{ v }}
        </v-col>
      </v-row>
      <h3 class="my-5">
        Report Header
      </h3>
      <v-row
        v-for="(v, k, n) in items.headers"
        :key="k"
        :class="n % 2 ? 'bg-surface-light' : ''"
      >
        <v-col
          cols="12"
          md="2"
        >
          {{ k }}
        </v-col>
        <v-col
          cols="12"
          md="10"
        >
          {{ v }}
        </v-col>
      </v-row>
    </v-tabs-window-item>
    <v-tabs-window-item value="result">
      <v-data-table
        :headers="headers"
        :items="items.messages ?? []"
        :items-per-page="-1"
        :mobile="null"
      >
        <template #item.level="{ value }">
          <v-icon
            :color="colorMap[value]"
            :icon="'mdi-' + iconMap[value]"
          />
        </template>
      </v-data-table>
    </v-tabs-window-item>
  </v-tabs-window>
</template>

<script setup lang="ts">
const tab = ref(null)

const items = ref([])
const route = useRoute()
const headers = [
	{ key: "level" },
	{ key: "header", title: "Position" },
	{ key: "data", title: "Data" },
	{ key: "message", title: "Message" },
]
const headers2 = [
	{ key: "0", title: "" },
	{ key: "1", title: "", align: "left" },
]
const iconMap = {
	0: "check",
	1: "information-slab-circle-outline",
	2: "exclamation-thick",
	3: "close-thick",
	4: "octagon",
	5: "skull-crossbones",
}
const colorMap = {
	0: "success",
	1: "info",
	2: "warning",
	3: "error",
	4: "error",
	5: "error",
}
const info = computed(() => ({
	"File name": items.value.filename,
	"Created": items.value.created,
	"Memory consumed": items.value.memory,
}))

async function load() {
	const response = await fetch(`/api/validation/${route.params.path}/`)
	items.value = (await response.json())
}
load().then()
</script>
