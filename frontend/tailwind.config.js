/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#090b0e',
        surface: '#11151c',
        surfaceHover: '#181d26',
        surfaceLight: '#212733',
        borderMuted: '#222834',
        accent: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          amber: '#f59e0b',
          teal: '#14b8a6',
          crimson: '#e11d48'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 8px 30px rgba(0, 0, 0, 0.45)',
        'glow': '0 0 40px -10px rgba(99, 102, 241, 0.25)',
      }
    },
  },
  plugins: [],
}

