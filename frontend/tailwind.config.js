/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}", "./public/index.html"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0A0A0A",
          hover: "#27272A",
        },
        canvas: {
          DEFAULT: "#FFFFFF",
          subtle: "#F9FAFB",
          muted: "#F3F4F6",
        },
        line: {
          DEFAULT: "#E5E7EB",
          strong: "#D1D5DB",
        },
      },
      fontFamily: {
        heading: ["Chivo", "sans-serif"],
        body: ["IBM Plex Sans", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
