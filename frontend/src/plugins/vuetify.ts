/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import "@mdi/font/css/materialdesignicons.css"
import "vuetify/styles"

// Composables
import { createVuetify, type ThemeDefinition } from "vuetify"

const dark: ThemeDefinition = {
	dark: true,
	colors: {
		background: "#000000",
		// surface: "#000000",
	},
}

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
	theme: {
		// defaultTheme: 'dark',
		themes: {
			dark,
		},
	},
	defaults: {
		VSheet: { color: "background" },
	},
})
