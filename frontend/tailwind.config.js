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
          greenHover: '#6d9b3a',
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
    },
  },
  plugins: [],
}
