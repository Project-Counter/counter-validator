// Plugins
import AutoImport from "unplugin-auto-import/vite"
import Components from "unplugin-vue-components/vite"
import Fonts from "unplugin-fonts/vite"
import Layouts from "vite-plugin-vue-layouts"
import Vue from "@vitejs/plugin-vue"
import VueRouter from "unplugin-vue-router/vite"
import Vuetify, { transformAssetUrls } from "vite-plugin-vuetify"
import vueDevTools from "vite-plugin-vue-devtools"
import legacy from "@vitejs/plugin-legacy"

// Utilities
import { defineConfig } from "vite"
import { fileURLToPath, URL } from "node:url"

// Version
import pkg from "./package.json"

process.env.VITE_APP_VERSION = pkg.version

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    legacy({
      targets: ["defaults", "not IE 11"],
      renderLegacyChunks: true,
      modernPolyfills: true,
    }),
    VueRouter({
      dts: "src/typed-router.d.ts",
      // default language for <route> custom blocks
      routeBlockLang: "yaml",
    }),
    vueDevTools(),
    Layouts(),
    AutoImport({
      imports: [
        "vue",
        {
          "vue-router/auto": ["useRoute", "useRouter"],
        },
      ],
      dts: "src/auto-imports.d.ts",
      eslintrc: {
        enabled: true,
      },
      vueTemplate: true,
    }),
    Components({
      dts: "src/components.d.ts",
    }),
    Vue({
      template: { transformAssetUrls },
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
    Vuetify({
      autoImport: true,
      styles: {
        configFile: "src/styles/settings.scss",
      },
    }),
    Fonts({
      google: {
        families: [
          {
            name: "Roboto",
            styles: "wght@100;300;400;500;700;900",
          },
        ],
      },
    }),
  ],
  define: { "process.env": {} },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
    extensions: [".js", ".json", ".jsx", ".mjs", ".ts", ".tsx", ".vue"],
  },
  server: {
    port: 3000,
    proxy: {
      "/api/": {
        target: `http://127.0.0.1:${process.env.VITE_BE_PORT || 8000}/`,
        changeOrigin: true,
      },
      "/media/": {
        target: `http://127.0.0.1:${process.env.VITE_BE_PORT || 8000}/`,
      },
    },
  },
  // the following should make is faster and get rid of unwanted reloads due
  // to code optimization
  optimizeDeps: { exclude: ["vuetify"] },
  css: {
    preprocessorOptions: {
      scss: {
        api: "modern",
      },
      sass: {
        api: "modern",
      },
    },
    preprocessorMaxWorkers: true,
  },
  build: {
    sourcemap: true,
  },
})
