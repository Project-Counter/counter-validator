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
				v-for="(v, k, n) in items?.result.header"
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
				:items="items?.result.messages"
				:headers="headers"
				:items-per-page="-1"
				:mobile="null"
				:cell-props="({item, column}) => (column.key == 'color' ? {class: 'bg-' + colorMap[item.l], style: {minHeight: '4px'}} : {})"
			/>
		</v-tabs-window-item>
	</v-tabs-window>
</template>

<script setup lang="ts">
import { ValidationDetail } from "@/lib/definitions/api"
import { getValidationDetail } from "@/lib/http/validation"

const tab = ref(null)

const items = ref<ValidationDetail>()
const route = useRoute()
const headers = [
	{ key: "color", title: "", sortable: false },
	{ key: "l", title: "Level" },
	{ key: "p", title: "Position" },
	{ key: "m", title: "Message" },
	{ key: "h", title: "Hint" },
]
const colorMap: Record<string, string> = {
	"Passed": "success",
	"Notice": "info",
	"Warning": "warning",
	"Error": "error",
	"Critical error": "error",
	"Fatal error": "error",
}
const info = computed(() => ({
	"File name": items.value?.filename,
	"Created": items.value?.created,
}))

async function load() {
	items.value = await getValidationDetail(route.params.path)
}
load().then()
</script>
