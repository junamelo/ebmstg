/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'moov-orange': '#FF6600',
        'moov-orange-dark': '#cc5200',
        'moov-orange-light': '#ff8533',
        'moov-blue': '#003087',
        'moov-blue-light': '#0052cc',
        'moov-gray-light': '#f5f5f5',
        'moov-gray': '#e0e0e0',
        'moov-gray-dark': '#666666',
        'moov-text': '#1a1a1a',
        'moov-success': '#28a745',
        'moov-danger': '#dc3545',
        'moov-warning': '#ffc107',
      },
      animation: {
        'shimmer': 'shimmer 2s infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        shimmer: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
}
