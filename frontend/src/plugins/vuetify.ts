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
    secondary: "#0085c1",
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
    VAlert: { variant: "tonal" },
    VDataTableServer: {
      itemsPerPageOptions: [10, 25, 50, 100],
      showAll: false,
    },
  },
})
