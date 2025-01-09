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

const counterBlue = "#273582"

const light: ThemeDefinition = {
  variables: {
    "high-emphasis-opacity": 1,
    "medium-emphasis-opacity": 0.7,
    "disabled-opacity": 0.5,
  },
  colors: {
    primary: counterBlue,
    secondary: "#bfe4f1",
    subdued: "#707070",
  },
}

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: "light",
    themes: {
      light,
    },
  },
  defaults: {
    VSheet: { color: "background" },
  },
})
