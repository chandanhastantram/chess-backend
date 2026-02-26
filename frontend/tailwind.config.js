/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Chess.com standard palette
        board: {
          light: '#ebecd0',   // cream/beige light squares
          dark: '#779556',    // green dark squares
          selected: '#f6f669', 
          move: '#baca44',    
          lastLight: '#f6f680',
          lastDark: '#bbcc44',
        },
        surface: {
          DEFAULT: '#312e2b',  // main dark brown-gray
          100: '#272421',      // darkest
          200: '#312e2b',      // primary surface
          300: '#3d3a37',      // card / elevated
          400: '#48453f',      // hover states
          500: '#5c5955',      // muted text bg
        },
        text: {
          DEFAULT: '#ededed',   // primary text
          muted: '#a0a0a0',     // secondary text
          dim: '#7c7c7c',       // tertiary text
        },
        accent: {
          green: '#81b64c',     // chess.com green (buttons, success)
          greenHover: '#a3d160', // brighter green for hover
          greenDark: '#5a8728',
          orange: '#e58f2a',    // rating / premium
          red: '#e02828',       // danger / blunder
          yellow: '#f0c340',    // inaccuracy
        },
        eval: {
          brilliant: '#1baca6',
          great: '#5c8bb0',
          best: '#96bc4b',
          good: '#96bc4b',
          inaccuracy: '#f0c340',
          mistake: '#e69d00',
          blunder: '#ca3531',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['Roboto Mono', 'Consolas', 'monospace'],
      },
      borderRadius: {
        'board': '4px',
      },
      animation: {
        'pop': 'pop 0.2s ease-out forwards',
        'subtle-pulse': 'subtle-pulse 2s infinite',
        'slide-up': 'slide-up 0.3s ease-out forwards',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 3s ease-in-out infinite',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'bounce-in': 'bounce-in 0.5s ease-out forwards',
        'fade-in-up': 'fade-in-up 0.4s ease-out forwards',
        'scale-in': 'scale-in 0.3s ease-out forwards',
        'piece-place': 'piece-place 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
      },
      keyframes: {
        pop: {
          '0%': { transform: 'scale(0.95)', opacity: '0.5' },
          '50%': { transform: 'scale(1.02)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'subtle-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 5px rgba(129, 182, 76, 0.2)' },
          '50%': { boxShadow: '0 0 20px rgba(129, 182, 76, 0.4), 0 0 40px rgba(129, 182, 76, 0.1)' },
        },
        'bounce-in': {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.95)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'fade-in-up': {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'piece-place': {
          '0%': { transform: 'scale(0) rotate(-180deg)', opacity: '0' },
          '100%': { transform: 'scale(1) rotate(0deg)', opacity: '1' },
        },
      }
    },
  },
  plugins: [],
}
