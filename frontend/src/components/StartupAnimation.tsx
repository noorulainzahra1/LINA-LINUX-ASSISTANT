/**
 * Startup Animation Component
 * Cyberpunk-style LINA logo animation with glitch effects and neon glow
 */
import { useEffect, useState } from 'react';

interface StartupAnimationProps {
  onComplete: () => void;
}

export default function StartupAnimation({ onComplete }: StartupAnimationProps) {
  const [showText, setShowText] = useState(false);
  const [letters, setLetters] = useState<string[]>([]);
  const [displayedLetters, setDisplayedLetters] = useState<string[]>([]);
  const [showGlitch, setShowGlitch] = useState(false);

  useEffect(() => {
    // Initialize letters
    const linaLetters = ['L', 'I', 'N', 'A'];
    setLetters(linaLetters);

    // Sequence: Fade in background → Typewriter effect → Glitch → Complete
    const timer1 = setTimeout(() => setShowText(true), 200);
    
    // Typewriter effect
    let letterIndex = 0;
    const typewriter = setInterval(() => {
      if (letterIndex < linaLetters.length) {
        setDisplayedLetters(prev => [...prev, linaLetters[letterIndex]]);
        letterIndex++;
      } else {
        clearInterval(typewriter);
        // Trigger glitch effects
        setShowGlitch(true);
        // Complete animation
        setTimeout(() => {
          onComplete();
        }, 1500);
      }
    }, 300);

    return () => {
      clearTimeout(timer1);
      clearInterval(typewriter);
    };
  }, [onComplete]);

  return (
    <div className="fixed inset-0 bg-gradient-light dark:bg-gradient-dark flex items-center justify-center z-50 overflow-hidden">
      {/* Subtle background elements */}
      <div className="absolute inset-0 opacity-10 dark:opacity-20">
        <div className="h-full w-full" style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(59, 130, 246, 0.05) 2px, rgba(59, 130, 246, 0.05) 4px)',
          animation: 'scanline 8s linear infinite',
        }} />
      </div>

      {/* Subtle Decorative background blobs - NO purple in dark mode */}
      <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-cyber-blue/5 dark:bg-cyber-blue/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-[350px] h-[350px] bg-cyber-cyan/5 dark:bg-cyber-cyan/10 rounded-full blur-3xl" />

      {/* Main logo container */}
      <div className={`relative transition-opacity duration-500 ${showText ? 'opacity-100' : 'opacity-0'}`}>
        
        {/* Logo text */}
        <div className={`relative ${showGlitch ? 'animate-glitch' : ''}`}>
          <h1 className="text-9xl md:text-[12rem] font-black tracking-wider">
            <span className="bg-gradient-button bg-clip-text text-transparent">
              {letters.map((letter, index) => {
                const isDisplayed = displayedLetters.length > index;
                
                return (
                  <span
                    key={index}
                    className={`inline-block transition-all duration-300 ${
                      isDisplayed ? '' : 'opacity-0'
                    }`}
                    style={{
                      animation: isDisplayed && showGlitch ? 'glitch 0.1s' : 'none',
                    }}
                  >
                    {letter}
                  </span>
                );
              })}
            </span>
          </h1>
        </div>

        {/* Subtitle */}
        {displayedLetters.length === letters.length && (
          <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 w-full text-center">
            <p className="text-2xl md:text-3xl font-bold text-gray-700 dark:text-dark-text">
              AI-Powered Cybersecurity Assistant
            </p>
          </div>
        )}
      </div>

      <style>{`
        @keyframes scanline {
          0% { transform: translateY(0); }
          100% { transform: translateY(100vh); }
        }
      `}</style>
    </div>
  );
}

