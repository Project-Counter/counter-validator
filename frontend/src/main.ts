/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from "@/plugins"

// Components
import App from "./App.vue"

// Composables
import { createApp } from "vue"

const app = createApp(App)

registerPlugins(app)

app.mount("#app")

// This is a workaround for a Vite issue where the preload fails
// after a new version of the app is deployed.
window.addEventListener("vite:preloadError", (event) => {
  console.error("Vite preload error", event)
  window.location.reload()
})
