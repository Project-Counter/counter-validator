<template>
	<div class="d-flex flex-column align-center text-center ga-3">
		<v-icon
			icon="mdi-cloud-upload"
			size="64"
		/>
		<h2>Uploading</h2>
		<v-progress-linear
			v-model="progress"
			color="primary"
		/>
	</div>

	<v-list
		lines="two"
		class="my-6"
		max-height="55vh"
		border
	>
		<v-list-item
			v-for="(file, i) in fileHistory"
			:key="i"
			:title="file.filename"
		>
			<template #subtitle>
				Uploading
				<v-progress-circular
					v-if="uploading.has(file.filename)"
					color="grey"
					:size="18"
					indeterminate
				/>
				<template v-else-if="file.id !== undefined">
					done <v-icon
						icon="mdi-check"
						color="success"
					/>
				</template>
				<template v-else>
					failed <v-icon
						icon="mdi-alert"
						color="error"
					/>
				</template>

				<span
					v-if="file.status !== undefined"
					class="ml-2"
				>
					Status: <validation-status :value="file.status" />
				</span>
			</template>
		</v-list-item>
	</v-list>

	<div class="text-end">
		<v-slide-x-transition>
			<v-btn
				v-if="progress == 100"
				class="mb-3"
				color="primary"
				text="New validation"
				prepend-icon="mdi-plus"
				@click="back"
			/>
		</v-slide-x-transition>
	</div>
</template>

<script setup lang="ts">
/* A note about data flow:
 * This component may recieve readable browser File objects through the prop `props.files`,
 * which it will then try to upload. This component also tracks uploaded, uploading or failed
 * props.files through a localstorage-backed store property `fileHistory.value`, so the user can
 * open a detail of the validated file and then return back to this list of props.files
 * that were uploaded in a batch.
 */

import { Status } from "@/lib/definitions/api"
import { FUpload } from "@/lib/definitions/upload"
import { getValidation, validateFile } from "@/lib/http/validation"
import { useAppStore } from "@/stores/app"
import { useTimeoutPoll } from "@vueuse/core"
import { storeToRefs } from "pinia"

/*
 * `props.files` is only used for init - they are copied to `fileHistory.value`.
 * Every file is in `fileHistory.value` and:
 * - is in `uploading` => is being uploaded,
 * - has `id`, `status` in `fileHistory.value` => uploaded succesfully (watching validation),
 * - else => failed upload.
 */

const store = useAppStore()
const { fileHistory } = storeToRefs(store)

const emit = defineEmits(["back"])
const props = defineProps<{
	files: FUpload[]
}>()
const uploading = reactive(new Set())
const progress = computed(() => (fileHistory.value.length - uploading.size) / fileHistory.value.length * 100)

function back() {
	fileHistory.value.length = 0
	emit("back")
}

async function checkValidation() {
	for (const file of fileHistory.value) {
		if (!file.id || file.status! > Status.RUNNING) {
			continue
		}
		try {
			file.status = (await getValidation(file.id.toString())).status
		}
		catch (err) {
			if (err instanceof DOMException && err.name === "AbortError") return
			throw err
		}
	}
}

async function upload(file: FUpload) {
	try {
		const res = await validateFile(file)
		const fh = fileHistory.value.find(el => el.filename == file.file.name)
		fh!.id = res.id
		fh!.status = res.status
	}
	catch (err) {
		// TODO: ...
	}
	finally {
		uploading.delete(file.file.name)
	}
}
if (props.files.length) {
	fileHistory.value.length = 0
	for (const file of props.files) {
		fileHistory.value.push({ filename: file.file.name })
		uploading.add(file.file.name)
	}
	for (const file of props.files) {
		upload(file).then()
	}
}

if (fileHistory.value.length == 0) {
	back() // no props.files to show, go back to the filepicker form
}

useTimeoutPoll(checkValidation, 1000, {
	immediate: true,
})

</script>
