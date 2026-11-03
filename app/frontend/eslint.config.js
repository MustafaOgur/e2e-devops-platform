import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";

export default [
  { ignores: ["dist/", "coverage/"] },
  js.configs.recommended,
  reactHooks.configs.flat.recommended,
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    rules: {
      // ESLint JSX içindeki kullanımı görmez: <App /> kullanılmıyor sanılmasın
      "no-unused-vars": ["error", { varsIgnorePattern: "^[A-Z]" }],
    },
  },
];
