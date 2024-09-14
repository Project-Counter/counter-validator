<template>
	<v-sheet
		class="mx-auto pa-4"
		rounded
		width="480"
	>
		<h2 class="mb-3">
			COUNTER Validation Tool
		</h2>
		<v-form
			validate-on="invalid-input"
			@submit.prevent="doLogin"
		>
			<v-row>
				<v-col>
					<v-text-field
						v-if="page == Page.Signup"
						counter
						label="First name"
						:maxlength="150"
						:rules="[rules.required]"
						variant="outlined"
					/>
				</v-col>
				<v-col>
					<v-text-field
						v-if="page == Page.Signup"
						counter
						label="Last name"
						:maxlength="150"
						:rules="[rules.required]"
						variant="outlined"
					/>
				</v-col>
			</v-row>
			<v-text-field
				v-model="email"
				:autofocus="true"
				class="mt-3"
				counter
				label="Email address"
				:maxlength="254"
				prepend-inner-icon="mdi-email"
				:rules="[rules.required, rules.email]"
				variant="outlined"
				@keyup.enter.stop="doLogin"
			/>
			<v-text-field
				v-if="page != Page.Forgotten"
				v-model="password"
				:append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
				class="mt-3"
				label="Password"
				prepend-inner-icon="mdi-key"
				:rules="[rules.required]"
				:type="showPassword ? 'text' : 'password'"
				variant="outlined"
				@click:append-inner="showPassword = !showPassword"
				@keyup.enter.stop="doLogin"
			/>
			<v-text-field
				v-if="page == Page.Signup"
				v-model="password2"
				class="mt-3"
				:disabled="showPassword"
				label="Password (again)"
				prepend-inner-icon="mdi-key"
				:rules="[rules.required]"
				type="password"
				variant="outlined"
				@keyup.enter.stop="doLogin"
			/>
			<v-btn
				block
				:text="page"
				class="mt-4"
				color="primary"
				:disabled="loading"
				:loading="loading"
				type="submit"
			/>

			<div class="d-flex justify-space-between mt-3">
				<v-btn
					v-if="page != Page.Login"
					:text="Page.Login"
					color="primary"
					variant="outlined"
					@click="page = Page.Login"
				/>
				<v-btn
					v-if="page != Page.Signup"
					:text="Page.Signup"
					color="primary"
					variant="outlined"
					@click="page = Page.Signup"
				/>
				<v-btn
					v-if="page != Page.Forgotten"
					:text="Page.Forgotten"
					color="primary"
					variant="text"
					@click="page = Page.Forgotten"
				/>
			</div>
		</v-form>
	</v-sheet>
</template>

<script setup lang="ts">
import { login, signup } from "@/lib/http/auth"
import * as rules from "@/lib/formRules"

enum Page {
	Login = "Sign in",
	Signup = "Create account",
	Forgotten = "Forgot password?",
}

const page = ref(Page.Login)
const email = ref("")
const password = ref("")
const password2 = ref("")
const showPassword = ref(false)
const loading = ref(false)

watchEffect(() => {
	if (showPassword.value) {
		password2.value = password.value
	}
})

async function doLogin() {
	loading.value = true
	try {
		switch (page.value) {
			case Page.Login:
				await login(email.value, password.value)
				break
			case Page.Signup:
				await signup(email.value, password.value, password.value)
				break
		}
	}
	finally {
		loading.value = false
	}
}
</script>
