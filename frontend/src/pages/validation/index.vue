<template>
	<v-data-table
		:headers="headers"
		:items="items"
		:mobile="null"
		no-data-text="No validations in your history"
	>
		<template #item.status="{ value }">
			<validation-status :value="value" />
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
import { Validation } from "@/lib/definitions/api"
import { getValidations } from "@/lib/http/validation"

const compare = new Intl.Collator().compare

const items = ref<Validation[]>([])
const headers = [
	{ key: "status", title: "Status", align: "center", width: 1 },
	{ key: "filename", title: "Filename" },
	{ key: "platform", title: "Platform", sortRaw(a: Validation, b: Validation) {
		const platformA = a.platform ?? a.platform_name
		const platformB = b.platform ?? b.platform_name
		return compare(platformA, platformB)
	} },
	{ key: "detail", title: "Detail", sortable: false },
	{ key: "id", title: "Time" },
]

async function load() {
	items.value = await getValidations()
}
load().then()
</script>
