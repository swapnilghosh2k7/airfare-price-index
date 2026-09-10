/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#0b192c',
          header: '#1e293b',
          blue: '#1e3a8a',
          accent: '#2563eb',
          gold: '#d97706',
          slate: '#334155',
          light: '#f8fafc',
          border: '#e2e8f0'
        }
      }
    },
  },
  plugins: [],
}
