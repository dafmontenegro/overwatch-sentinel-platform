/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        white: '#FFFFFF',
        asphalt: '#0C0404',
        capri: '#00BFFF',
        whitegray: '#F2F3F5',
        // Variantes de los colores principales
        caprilight: '#66D9FF',
        capridark: '#0099CC',
        asphaltlight: '#2D2525',
        asphaltdark: '#070202',
      }
    }
  },
  plugins: [],
}