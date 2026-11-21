/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(220 10% 25%)',
        input: 'hsl(220 10% 25%)',
        ring: 'hsl(220 80% 60%)',
        primary: {
          DEFAULT: 'hsl(220 80% 60%)',
          foreground: 'hsl(0 0% 100%)',
        },
        secondary: {
          DEFAULT: 'hsl(220 70% 60%)',
          foreground: 'hsl(0 0% 100%)',
        },
        destructive: {
          DEFAULT: 'hsl(0 80% 60%)',
          foreground: 'hsl(0 0% 100%)',
        },
        muted: {
          DEFAULT: 'hsl(220 10% 15%)',
          foreground: 'hsl(220 10% 60%)',
        },
        accent: {
          DEFAULT: 'hsl(220 80% 65%)',
          foreground: 'hsl(0 0% 100%)',
        },
      },
      borderRadius: {
        lg: '0.5rem',
        DEFAULT: 'var(--radius)',
        md: 'var(--radius) - 4px',
        sm: 'var(--radius) - 6px',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};