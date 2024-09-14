<template>
	<v-dialog
		v-model="dialog"
		activator="parent"
		:max-width="500"
	>
		<template #default="{ isActive }">
			<v-card title="API key revocation">
				<v-card-text>
					<p>Are you sure you want to <strong>revoke</strong> the API key beggining with <code class="bg-surface-light pa-1 rounded">{{ props.prefix }}</code>?</p>
					<p class="mt-3 text-caption">
						This cannot be undone and the API key will never work again!
					</p>
				</v-card-text>

				<v-card-actions>
					<v-btn
						text="Cancel"
						@click="isActive.value = false"
					/>
					<v-spacer />
					<v-btn
						color="error"
						:loading="loading"
						text="Revoke"
						variant="tonal"
						@click="revoke"
					/>
				</v-card-actions>
			</v-card>
		</template>
	</v-dialog>
</template>

<script setup lang="ts">
import { revokeApiKey } from "@/lib/http/auth"

const emit = defineEmits(["update"])
const props = defineProps<{
	prefix: string
}>()

const dialog = ref(false)
const loading = ref(false)

async function revoke() {
	loading.value = true
	await revokeApiKey(props.prefix)
	loading.value = false
	emit("update")
	dialog.value = false
}
</script>
