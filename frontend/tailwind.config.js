/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        /**
         * Brand palette. We deliberately OVERRIDE Tailwind's built-in `teal`
         * (the app's existing accent) with a refined medical teal–cyan so every
         * existing `teal-*` utility across all pages adopts the new identity at
         * once. `brand` is an explicit alias for new code.
         */
        teal: {
          50: '#ecfdfb',
          100: '#cff9f3',
          200: '#a1f1e9',
          300: '#67e3d9',
          400: '#2fccc3',
          500: '#12b1a9',
          600: '#068f8a',
          700: '#0a726f',
          800: '#0d5b59',
          900: '#104b4a',
          950: '#022e2e',
        },
        brand: {
          50: '#ecfdfb',
          100: '#cff9f3',
          200: '#a1f1e9',
          300: '#67e3d9',
          400: '#2fccc3',
          500: '#12b1a9',
          600: '#068f8a',
          700: '#0a726f',
          800: '#0d5b59',
          900: '#104b4a',
          950: '#022e2e',
        },
        accent: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },
      },
      fontFamily: {
        sans: ['Inter var', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        xl: '0.875rem',
        '2xl': '1.125rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        soft: '0 1px 2px 0 rgb(15 23 42 / 0.04), 0 1px 3px 0 rgb(15 23 42 / 0.06)',
        card: '0 1px 3px rgb(15 23 42 / 0.06), 0 8px 24px -12px rgb(15 23 42 / 0.12)',
        elevated: '0 12px 32px -8px rgb(15 23 42 / 0.18)',
        glow: '0 0 0 1px rgb(6 143 138 / 0.12), 0 12px 32px -8px rgb(6 143 138 / 0.35)',
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #068f8a 0%, #12b1a9 55%, #2fccc3 100%)',
        'brand-radial': 'radial-gradient(60% 60% at 50% 0%, rgb(103 227 217 / 0.25) 0%, transparent 70%)',
        'mesh': 'radial-gradient(at 0% 0%, rgb(103 227 217 / 0.18) 0px, transparent 55%), radial-gradient(at 100% 0%, rgb(129 140 248 / 0.14) 0px, transparent 50%), radial-gradient(at 80% 100%, rgb(47 204 195 / 0.12) 0px, transparent 45%)',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        shimmer: {
          '100%': { transform: 'translateX(100%)' },
        },
        'pulse-ring': {
          '0%': { transform: 'scale(0.9)', opacity: '0.7' },
          '70%, 100%': { transform: 'scale(1.6)', opacity: '0' },
        },
        'scan-sweep': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(400%)' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.5s cubic-bezier(0.22, 1, 0.36, 1) both',
        float: 'float 5s ease-in-out infinite',
        shimmer: 'shimmer 2s infinite',
        'pulse-ring': 'pulse-ring 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite',
        'scan-sweep': 'scan-sweep 2.6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
