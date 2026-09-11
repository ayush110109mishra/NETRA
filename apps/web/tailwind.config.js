/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        tactical: {
          bg: '#070b12',
          surface: '#0d131f',
          panel: '#111927',
          header: '#0a0f1a',
          border: '#1e293b',
          borderHover: '#334155',
          borderAccent: 'rgba(6, 182, 212, 0.4)',
        },
        defence: {
          cyan: '#06b6d4',
          'cyan-bright': '#22d3ee',
          'cyan-dim': 'rgba(6, 182, 212, 0.15)',
          green: '#10b981',
          'green-dim': 'rgba(16, 185, 129, 0.15)',
          amber: '#f59e0b',
          'amber-dim': 'rgba(245, 158, 11, 0.15)',
          red: '#ef4444',
          'red-dim': 'rgba(239, 68, 68, 0.15)',
          muted: '#64748b',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'tactical-sm': '0 1px 3px 0 rgba(0, 0, 0, 0.5)',
        'tactical-glow': '0 0 15px rgba(6, 182, 212, 0.12)',
        'tactical-card': '0 4px 12px 0 rgba(0, 0, 0, 0.6)',
      },
      animation: {
        'radar-sweep': 'radarSweep 4s linear infinite',
        'pulse-subtle': 'pulseSubtle 2.5s ease-in-out infinite',
      },
      keyframes: {
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
      },
    },
  },
  plugins: [],
};
