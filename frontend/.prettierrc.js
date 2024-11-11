"use strict"

module.exports = {
  excludeFiles: "*.d.ts",
  overrides: [
    {
      files: "*.{js,ts,vue,mts}",
      options: {
        semi: false,
        singleAttributePerLine: true,
      },
    },
  ],
}
