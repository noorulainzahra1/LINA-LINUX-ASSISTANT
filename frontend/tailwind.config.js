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
        // VIBRANT LIGHT THEME - Colorful, Modern, Professional
        light: {
          bg: '#FFFFFF', // Pure white (primary background)
          'bg-alt': '#F8FAFC', // Off-white (secondary background)
          'bg-secondary': '#F1F5F9', // Very light gray (cards, panels)
          'bg-tertiary': '#E2E8F0', // Light gray (input backgrounds)
          'bg-hover': '#E0E7FF', // Light blue hover state
          'bg-gradient-start': '#FFFFFF', // Gradient start
          'bg-gradient-end': '#F8FAFC', // Gradient end
          border: '#E2E8F0', // Light gray border
          'border-light': '#F1F5F9', // Very light gray border
          'border-accent': '#3B82F6', // Vibrant blue border
        },
        cyber: {
          blue: '#3B82F6', // Electric Blue
          'blue-deep': '#2563EB', // Deep Electric Blue
          'blue-darker': '#1D4ED8', // Darker Electric Blue
          cyan: '#06B6D4', // Bright Cyan
          purple: '#A855F7', // Vibrant Purple
          'purple-light': '#C084FC', // Light Purple
          pink: '#EC4899', // Hot Pink
          green: '#10B981', // Bright Green
          yellow: '#F59E0B', // Amber
          orange: '#F97316', // Orange
        },
        accent: {
          lavender: '#A855F7', // Vibrant Purple
          aqua: '#06B6D4', // Bright Cyan
          purple: '#C084FC', // Light Purple
          pink: '#EC4899', // Hot Pink
          gray: '#94A3B8', // Light slate gray
        },
        action: {
          red: '#EF4444', // Bright Red
          gold: '#F59E0B', // Amber
        },
        terminal: {
          green: '#10B981', // Bright terminal green
        },
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        // DARK MODE COLORS - NO purple/pink
        dark: {
          bg: '#0F172A', // Dark slate (primary background)
          'bg-alt': '#1E293B', // Slate-800 (secondary background)
          'bg-secondary': '#334155', // Slate-700 (cards, panels)
          'bg-tertiary': '#475569', // Slate-600 (input backgrounds)
          'bg-hover': '#475569', // Hover state
          'bg-gradient-start': '#0F172A', // Gradient start
          'bg-gradient-end': '#1E293B', // Gradient end
          border: '#475569', // Border color
          'border-light': '#64748B', // Light border
          'border-accent': '#3B82F6', // Blue accent border
          text: '#F1F5F9', // Primary text
          'text-secondary': '#E2E8F0', // Secondary text
          'text-muted': '#CBD5E1', // Muted text
        },
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'glitch': 'glitch 0.3s ease-in-out',
        'typing': 'typing 0.5s steps(40, end)',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { 
            opacity: '1',
            filter: 'drop-shadow(0 0 20px rgba(59, 130, 246, 0.8))',
          },
          '50%': { 
            opacity: '0.8',
            filter: 'drop-shadow(0 0 40px rgba(59, 130, 246, 1))',
          },
        },
        'glitch': {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
        },
        'typing': {
          'from': { width: '0' },
          'to': { width: '100%' },
        },
        'gradient': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
      boxShadow: {
        'stealth': '0 0 20px rgba(168, 85, 247, 0.4)',
        'stealth-lg': '0 0 40px rgba(168, 85, 247, 0.5)',
        'digital': '0 0 30px rgba(59, 130, 246, 0.5)',
        'digital-lg': '0 0 50px rgba(59, 130, 246, 0.6)',
        'glow': '0 0 40px rgba(59, 130, 246, 0.6)',
        'glow-blue': '0 0 30px rgba(59, 130, 246, 0.8), 0 0 60px rgba(59, 130, 246, 0.4), 0 8px 16px rgba(0, 0, 0, 0.4)',
        'glow-purple': '0 0 30px rgba(168, 85, 247, 0.8), 0 0 60px rgba(168, 85, 247, 0.4), 0 8px 16px rgba(0, 0, 0, 0.4)',
        'glow-cyan': '0 0 30px rgba(6, 182, 212, 0.8), 0 0 60px rgba(6, 182, 212, 0.4), 0 8px 16px rgba(0, 0, 0, 0.4)',
        'glow-pink': '0 0 30px rgba(236, 72, 153, 0.8), 0 0 60px rgba(236, 72, 153, 0.4), 0 8px 16px rgba(0, 0, 0, 0.4)',
        'glow-orange': '0 0 30px rgba(249, 115, 22, 0.8), 0 0 60px rgba(249, 115, 22, 0.4), 0 8px 16px rgba(0, 0, 0, 0.4)',
        'glow-green': '0 0 30px rgba(16, 185, 129, 0.8), 0 0 60px rgba(16, 185, 129, 0.4), 0 8px 16px rgba(0, 0, 0, 0.4)',
        'light': '0 4px 6px rgba(0, 0, 0, 0.3)',
        'light-md': '0 8px 16px rgba(0, 0, 0, 0.4)',
        'card': '0 8px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(59, 130, 246, 0.3)',
        'card-hover': '0 16px 48px rgba(0, 0, 0, 0.6), 0 0 40px rgba(59, 130, 246, 0.5)',
        'input-focus': '0 0 0 3px rgba(59, 130, 246, 0.5), 0 0 20px rgba(59, 130, 246, 0.6)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
        'glass-lg': '0 16px 64px 0 rgba(0, 0, 0, 0.6)',
        'neon': '0 0 20px currentColor, 0 0 40px currentColor, 0 0 80px currentColor',
      },
      backgroundImage: {
        'gradient-light': 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 50%, #FFFFFF 100%)',
        'gradient-dark': 'linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%)',
        'gradient-card': 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
        'gradient-card-dark': 'linear-gradient(135deg, #1E293B 0%, #334155 100%)',
        'gradient-button': 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #EC4899 100%)',
        'gradient-button-dark': 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 50%, #F59E0B 100%)',
        'gradient-button-hover': 'linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #DB2777 100%)',
        'gradient-button-hover-dark': 'linear-gradient(135deg, #2563EB 0%, #0891B2 50%, #F97316 100%)',
        'gradient-purple': 'linear-gradient(135deg, #A855F7 0%, #EC4899 100%)',
        'gradient-cyan': 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
        'gradient-blue-cyan': 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)',
        'gradient-cyan-green': 'linear-gradient(135deg, #06B6D4 0%, #10B981 100%)',
        'gradient-blue-orange': 'linear-gradient(135deg, #3B82F6 0%, #F59E0B 100%)',
        'gradient-border': 'linear-gradient(90deg, #3B82F6, #A855F7, #EC4899, #06B6D4, #3B82F6)',
        'gradient-border-dark': 'linear-gradient(90deg, #3B82F6, #06B6D4, #10B981, #F59E0B, #3B82F6)',
        'gradient-glow': 'radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.15), transparent 70%)',
        'gradient-glow-dark': 'radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.2), transparent 70%)',
        'gradient-mesh': 'radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.1) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.1) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.1) 0px, transparent 50%), radial-gradient(at 0% 100%, rgba(6, 182, 212, 0.1) 0px, transparent 50%)',
        'gradient-mesh-dark': 'radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(6, 182, 212, 0.15) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.12) 0px, transparent 50%), radial-gradient(at 0% 100%, rgba(249, 115, 22, 0.12) 0px, transparent 50%)',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'glitch': 'glitch 0.3s ease-in-out',
        'typing': 'typing 0.5s steps(40, end)',
        'gradient': 'gradient 8s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}

