import path from "node:path";
import { fileURLToPath } from "node:url";
import { FlatCompat } from "@eslint/eslintrc";
import pluginVue from "eslint-plugin-vue";
import js from "@eslint/js";
import ts from "typescript-eslint";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

export default [
  ...compat.extends("@vue/eslint-config-typescript", "./.eslintrc-auto-import.json"),
  js.configs.recommended,
  ...ts.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  {
    files: ["*.vue", "**/*.vue"],
    languageOptions: {
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
    },
  },
  {
    rules: {
      "vue/multi-word-component-names": "off",
      "vue/valid-v-slot": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "no-warning-comments": "warn",
    },
  },
  {
    ignores: ["dist/*", ".prettierrc.js", "**/*.d.ts"],
  },
  ...compat.extends("prettier"),
];
