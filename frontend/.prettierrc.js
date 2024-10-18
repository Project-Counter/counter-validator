"use strict"

module.exports = {
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
