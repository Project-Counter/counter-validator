<template>
  <v-data-table-virtual
    :headers="headers"
    :items="data"
    :mobile="null"
    mobile-breakpoint="sm"
    must-sort
    :sort-by="[{key: 'created', order: 'desc'}]"
  >
    <template #top>
      <v-sheet class="bg-surface-light d-flex align-center pa-4">
        <span class="text-caption">Your API keys<v-icon class="ml-4">mdi-key</v-icon> {{ data.length }}</span>
        <v-spacer />
        <v-btn size="small">
          Create a key
          <api-key-create @update="load" />
        </v-btn>
      </v-sheet>
    </template>
    <template #item.created="{ value }">
      <date-tooltip :date="value" />
    </template>
    <template #item.expiry_date="{ value }">
      <date-tooltip
        v-if="value"
        :date="value"
      />
      <span
        v-else
        class="text-disabled"
      >never</span>
    </template>
    <template #item.status="{ item }">
      <span
        v-if="item.revoked"
        class="text-error"
      >Revoked</span>
      <span
        v-else-if="item.has_expired"
        class="text-warning"
      >Expired</span>
      <span
        v-else
        class="text-success"
      >OK</span>
    </template>
    <template #item.actions="{ item }">
      <v-btn
        v-if="!item.revoked && !item.has_expired"
        color="error"
        size="small"
        variant="tonal"
      >
        Revoke
        <api-key-revoke
          :prefix="item.prefix"
          @update="load"
        />
      </v-btn>
    </template>
  </v-data-table-virtual>
</template>

<script setup lang="ts">
import { ApiKey } from "@/lib/definitions/ApiKey"
import { loadApiKeys } from "@/lib/http/auth"

const data: Ref<ApiKey[]> = ref([])
const headers = [
	{ key: "name", title: "Name", width: "30%" },
	{ key: "prefix", title: "Prefix" },
	{ key: "created", title: "Created" },
	{ key: "expiry_date", title: "Expiry" },
	{
		key: "status",
		title: "Status",
		sortRaw(a: ApiKey, b: ApiKey) {
			let av = 0
			let bv = 0
			if (a.revoked) av = 2
			else if (a.has_expired) av = 1
			if (b.revoked) bv = 2
			else if (b.has_expired) bv = 1

			if (av > bv) return 1
			else if (bv > av) return -1
			else return 0
		},
	},
	{ key: "actions", title: "Actions", sortable: false },
]

async function load() {
	data.value = await loadApiKeys()
}

load().then()
</script>

<style>
tbody {
	hyphens: auto;
	word-break: break-word;
}
</style>
