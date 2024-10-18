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

const light: ThemeDefinition = {
  variables: {
    "high-emphasis-opacity": 1,
    "medium-emphasis-opacity": 0.7,
    "disabled-opacity": 0.5,
  },
}
const dark: ThemeDefinition = {
  dark: true,
  colors: {
    background: "#000000",
  },
}

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    themes: {
      light,
      dark,
    },
    // variations: {
    //   colors: ['error', 'info'],
    //   lighten: 5,
    //   darken: 0,
    // },
  },
  defaults: {
    VSheet: { color: "background" },
  },
})
