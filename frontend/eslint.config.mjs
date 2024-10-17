import path from "node:path"
import { fileURLToPath } from "node:url"
import { FlatCompat } from "@eslint/eslintrc"
import stylistic from "@stylistic/eslint-plugin"
import migrate from "@stylistic/eslint-plugin-migrate"
import pluginVue from "eslint-plugin-vue"
import js from "@eslint/js"
import ts from "typescript-eslint"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
})

export default [
  ...compat.extends(
    // 	'vuetify',
    // 	// '@vue/eslint-config-typescript',
    "./.eslintrc-auto-import.json",
  ),
  js.configs.recommended,
  ...ts.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  stylistic.configs.customize({
    indent: 2,
    quotes: "double",

  }),
  {
    files: ["*.vue", "**/*.vue"],
    languageOptions: {
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
    },
  },
  {
    plugins: {
      "@stylistic": stylistic,
      "@stylistic/eslint-plugin-migrate": migrate,
    },

    rules: {
      "vue/multi-word-component-names": "off",
      "vue/valid-v-slot": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "@stylistic/indent": ["error", 2],
      "@stylistic/quotes": ["error", "double"],
      "no-warning-comments": "warn",
      "vue/html-indent": ["error", 2, {
        attribute: 1,
        baseIndent: 1,
        closeBracket: 0,
        alignAttributesVertically: true,
        ignores: [],
      }],
    },
  },
]
