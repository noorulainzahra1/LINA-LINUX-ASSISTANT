/**
 * Landing Page
 * First page users see - features Lina image and CTA buttons
 */
import { useNavigate } from 'react-router-dom';
import ThemeToggle from '../components/ThemeToggle';
import LinaImage from '../images/Lina.jpeg';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-light dark:bg-gradient-dark flex items-center justify-center p-4 custom-scrollbar relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-96 bg-gradient-glow dark:bg-gradient-glow-dark opacity-40 pointer-events-none" />
      <div className="absolute top-10 left-10 w-96 h-96 bg-cyber-blue/5 dark:bg-cyber-blue/10 rounded-full blur-3xl animate-float" />
      <div className="absolute top-40 right-20 w-80 h-80 bg-cyber-cyan/5 dark:bg-cyber-cyan/10 rounded-full blur-3xl animate-float" style={{animationDelay: '2s'}} />
      <div className="absolute bottom-20 left-20 w-72 h-72 bg-cyber-orange/5 dark:bg-cyber-orange/10 rounded-full blur-3xl animate-float" style={{animationDelay: '4s'}} />
      <div className="absolute bottom-40 right-10 w-96 h-96 bg-cyber-cyan/5 dark:bg-cyber-cyan/10 rounded-full blur-3xl animate-float" style={{animationDelay: '6s'}} />
      
      <div className="max-w-7xl w-full relative z-10">
        {/* Theme Toggle - Top Right */}
        <div className="absolute top-4 right-4 z-20">
          <ThemeToggle />
        </div>

        {/* Hero Section */}
        <div className="text-center">
          {/* LINA Title */}
          <div className="mb-12">
            <h1 className="text-8xl md:text-9xl font-black mb-4 tracking-tight bg-gradient-to-r from-cyber-blue via-cyber-cyan to-cyber-orange dark:from-cyber-blue dark:via-cyber-cyan dark:to-cyber-orange bg-clip-text text-transparent">
              LINA
            </h1>
            <div className="h-1.5 w-32 mx-auto rounded-full bg-gradient-to-r from-cyber-blue via-cyber-cyan to-cyber-orange" />
          </div>

          {/* Lina Image - Circular with Mysterious Glow */}
          <div className="mb-12 flex justify-center">
            <div className="relative group">
              {/* Outer glow layer - subtle and wide */}
              <div 
                className="absolute inset-0 w-64 md:w-80 lg:w-96 h-64 md:h-80 lg:h-96 rounded-full blur-3xl opacity-40 group-hover:opacity-60 transition-opacity duration-700"
                style={{
                  background: 'radial-gradient(circle, rgba(59, 130, 246, 0.6), rgba(6, 182, 212, 0.4), rgba(249, 115, 22, 0.3), transparent)',
                  transform: 'scale(1.3)',
                  animation: 'pulse 3s ease-in-out infinite',
                }}
              />
              
              {/* Middle glow layer - more intense */}
              <div 
                className="absolute inset-0 w-64 md:w-80 lg:w-96 h-64 md:h-80 lg:h-96 rounded-full blur-2xl opacity-50 group-hover:opacity-70 transition-opacity duration-700"
                style={{
                  background: 'radial-gradient(circle, rgba(59, 130, 246, 0.8), rgba(6, 182, 212, 0.6), transparent)',
                  transform: 'scale(1.15)',
                  animation: 'pulse 2s ease-in-out infinite',
                  animationDelay: '0.5s',
                }}
              />
              
              {/* Inner glow layer - brightest and closest */}
              <div 
                className="absolute inset-0 w-64 md:w-80 lg:w-96 h-64 md:h-80 lg:h-96 rounded-full blur-xl opacity-60 group-hover:opacity-80 transition-opacity duration-700"
                style={{
                  background: 'radial-gradient(circle, rgba(59, 130, 246, 1), rgba(6, 182, 212, 0.8), transparent)',
                  transform: 'scale(1.05)',
                  animation: 'pulse 1.5s ease-in-out infinite',
                  animationDelay: '1s',
                }}
              />
              
              {/* Circular image container */}
              <div className="relative w-64 md:w-80 lg:w-96 h-64 md:h-80 lg:h-96 rounded-full overflow-hidden border-4 border-cyber-blue/40 dark:border-cyber-blue/60 shadow-2xl transition-transform duration-500 group-hover:scale-105">
                <img
                  src={LinaImage}
                  alt="LINA - AI-Powered Cybersecurity Assistant"
                  className="w-full h-full object-cover"
                  style={{
                    filter: 'drop-shadow(0 0 40px rgba(59, 130, 246, 0.8))',
                  }}
                />
                {/* Subtle overlay for depth */}
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/10 rounded-full" />
              </div>
              
              {/* Animated ring effect */}
              <div 
                className="absolute inset-0 w-64 md:w-80 lg:w-96 h-64 md:h-80 lg:h-96 rounded-full border-2 border-cyber-blue/30 dark:border-cyber-blue/50 transition-all duration-700 group-hover:border-cyber-blue/60 dark:group-hover:border-cyber-blue/80"
                style={{
                  transform: 'scale(1.1)',
                  animation: 'pulse 2s ease-in-out infinite',
                }}
              />
            </div>
          </div>

          {/* Subtitle */}
          <div className="max-w-2xl mx-auto mb-12">
            <p className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-dark-text mb-4">
              AI-Powered Cybersecurity Assistant
            </p>
            <p className="text-lg md:text-xl text-gray-600 dark:text-dark-text-secondary">
              Your intelligent companion for cybersecurity operations, forensics, and penetration testing
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
            <button
              onClick={() => navigate('/login')}
              className="cyber-button px-8 py-4 text-lg font-bold flex items-center justify-center min-w-[200px]"
            >
              Login
            </button>
            <button
              onClick={() => navigate('/signup')}
              className="cyber-button-secondary px-8 py-4 text-lg font-bold flex items-center justify-center min-w-[200px]"
            >
              Sign Up
            </button>
          </div>

          {/* Footer */}
          <div className="text-center mt-16">
            <p className="text-gray-600 dark:text-dark-text-secondary text-base">
              Powered by <span className="font-semibold text-cyber-blue">Google Gemini AI</span> • <span className="font-semibold text-cyber-cyan dark:text-cyber-cyan">Phoenix Architecture</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

