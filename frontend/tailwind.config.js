/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0284c7',
          600: '#0369a1',
          900: '#0c4a6e',
        },
        risk: {
          low: '#10b981',     // emerald-500
          medium: '#f59e0b',  // amber-500
          high: '#f97316',    // orange-500
          critical: '#ef4444' // red-500
        }
      }
    },
  },
  plugins: [],
}
