/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "dark-orange": "#d9e2c9ff" // remove the extra "ff" at the end
      },
    },
  },
  plugins: [],
};

