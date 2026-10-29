/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#F7F8FA',
        primary: '#1F2937',
        'primary-dark': '#111827',
        secondary: '#4B5563',
        accent: '#2563EB',
        success: '#16A34A',
        warning: '#D97706',
        danger: '#DC2626',
        card: '#FFFFFF',
        border: '#E5E7EB',
        muted: '#6B7280'
      },
      borderRadius: {
        DEFAULT: '6px',
        md: '6px',
        lg: '8px'
      }
    },
  },
  plugins: [],
}

