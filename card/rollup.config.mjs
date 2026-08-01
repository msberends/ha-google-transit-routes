import typescript from "@rollup/plugin-typescript";
import resolve from "@rollup/plugin-node-resolve";
import terser from "@rollup/plugin-terser";

export default {
  input: "src/google-transit-routes-card.ts",
  output: {
    file: "../custom_components/google_transit_routes/www/google-transit-routes-card.js",
    format: "es",
    inlineDynamicImports: true,
  },
  plugins: [resolve(), typescript(), terser()],
};
