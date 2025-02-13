<template>
  <router-view />

  <v-snackbar
    v-model="errorShow"
    color="error"
    :timeout="-1"
    vertical
  >
    <div class="text-subtitle-1 pb-2"><v-icon class="mr-2"> mdi-alert </v-icon>Error!</div>

    <p>Sorry, there was an error. You may need to reload the app.</p>

    <template #actions>
      <v-btn>
        See details
        <msg-dialog title="Error log">
          <v-expansion-panels>
            <v-expansion-panel
              v-for="(err, i) in store.errors"
              :key="i"
              :title="err.err.toString()"
            >
              <template #text>
                <div>name: {{ err.err.name }}</div>
                <div>message: {{ err.err.message }}</div>
                <div>info: {{ err.info }}</div>
                <pre
                  class="py-4 text-caption"
                  style="overflow: scroll"
                  >{{ err.err.stack }}</pre
                >
              </template>
            </v-expansion-panel>
          </v-expansion-panels>
        </msg-dialog>
      </v-btn>
      <v-spacer />
      <v-btn
        text="Ignore"
        @click="errorShow = false"
      />
      <v-btn
        text="Reload"
        @click="reload"
      />
    </template>
  </v-snackbar>
  <v-snackbar
    v-if="store.notification"
    v-model="store.showNotification"
    :color="store.notification.type"
  >
    <p>
      <v-icon v-if="store.notification.type === 'error'">mdi-alert-circle-outline</v-icon>
      <v-icon v-else-if="store.notification.type === 'success'">mdi-check</v-icon>
      <v-icon v-else-if="store.notification.type === 'warning'">mdi-alert</v-icon>
      <v-icon v-else>mdi-information</v-icon>
      {{ store.notification.message }}
    </p>
  </v-snackbar>
</template>

<script setup lang="ts">
import { checkUser } from "@/lib/http/auth"
import { useAppStore } from "@/stores/app"
import { useTheme } from "vuetify"

const store = useAppStore()

const errorShow = ref(false)

function handleErr(err: Error, _: unknown, info: string) {
  store.errors.push({ err, info })
  errorShow.value = true
  return true
}

onErrorCaptured(handleErr)

checkUser().then()

function reload() {
  window.location.reload()
}

const theme = useTheme()
watch(
  () => store.darkTheme,
  (v) => {
    theme.global.name.value = v ? "dark" : "light"
  },
  { immediate: true },
)
</script>

<style>
.v-snackbar--vertical .v-snackbar__wrapper .v-snackbar__actions {
  width: 100%;
  padding-left: 8px;
  padding-right: 8px;
  margin-inline-end: 0;
}
</style>
