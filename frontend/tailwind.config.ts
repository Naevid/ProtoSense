import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17211f",
        graphite: "#35403d",
        mist: "#f5f7f6",
        line: "#d8e0dc",
        teal: "#187c74",
        mint: "#d9f2e9",
        coral: "#c95445",
        amber: "#b7791f"
      },
      boxShadow: {
        soft: "0 12px 30px rgba(23, 33, 31, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
