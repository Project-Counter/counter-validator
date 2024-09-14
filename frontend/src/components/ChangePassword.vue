<template>
	<v-dialog max-width="500">
		<template #activator="{ props: activatorProps }">
			<v-btn
				text="Change password"
				class="ml-2"
				v-bind="activatorProps"
			/>
		</template>

		<template #default="{ isActive }">
			<v-card title="Dialog">
				<v-card-text class="d-flex flex-column ga-1">
					<v-text-field
						label="Old password"
					/>
					<v-text-field
						label="New password"
					/>
					<v-text-field
						label="New password (again)"
					/>
				</v-card-text>

				<v-card-actions>
					<v-spacer />

					<v-btn
						text="Close Dialog"
						@click="isActive.value = false"
					/>
				</v-card-actions>
			</v-card>
		</template>
	</v-dialog>
</template>
