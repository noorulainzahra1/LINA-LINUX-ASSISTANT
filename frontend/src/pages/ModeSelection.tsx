/**
 * Mode Selection Page
 * Allows users to select their work mode after authentication
 */
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useSession } from '../contexts/SessionContext';
import { UserRole, WorkMode } from '../types';
import { Zap, MessageCircle, Lightbulb, ArrowLeft } from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';

const modes: Array<{
  id: WorkMode;
  icon: React.ReactNode;
  name: string;
  description: string;
  detailedDescription: string;
  color: string;
}> = [
  {
    id: 'quick',
    icon: <Zap className="w-12 h-12" />,
    name: 'Quick Mode',
    description: 'Execute commands instantly',
    detailedDescription: 'Minimal interaction, direct command execution with risk warnings only. Perfect for experienced users who know what they want.',
    color: 'border-cyber-blue hover:bg-cyber-blue/10 hover:shadow-digital',
  },
  {
    id: 'interactive',
    icon: <MessageCircle className="w-12 h-12" />,
    name: 'Interactive Mode',
    description: 'Real-time suggestions and guidance',
    detailedDescription: 'Get step-by-step guidance, real-time suggestions, and detailed explanations before execution. Ideal for learning and exploration.',
    color: 'border-cyber-cyan hover:bg-cyber-cyan/10 hover:shadow-digital dark:border-cyber-cyan dark:hover:bg-cyber-cyan/10',
  },
  {
    id: 'suggester',
    icon: <Lightbulb className="w-12 h-12" />,
    name: 'Command Suggester Mode',
    description: 'AI-powered command suggestions',
    detailedDescription: 'Receive intelligent command suggestions based on your input. Choose from multiple options before execution.',
    color: 'border-yellow-500 hover:bg-yellow-500/10 hover:shadow-digital',
  },
];

// Default role for now (can be made configurable later)
const DEFAULT_ROLE: UserRole = 'Student';

export default function ModeSelection() {
  const navigate = useNavigate();
  const { createSession, isLoading } = useSession();
  const [selectedMode, setSelectedMode] = useState<WorkMode | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelectMode = async (mode: WorkMode) => {
    setSelectedMode(mode);
    setError(null);

    try {
      // Create session with longer timeout (60 seconds for Brain initialization)
      const sessionPromise = createSession(DEFAULT_ROLE, mode);
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Session creation timed out after 60 seconds. The backend may be initializing. Please check if the API server is running.')), 60000)
      );
      
      await Promise.race([sessionPromise, timeoutPromise]);
      
      // Navigate immediately after session creation (status refresh happens in background)
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Session creation error:', err);
      const errorMsg = err.message || err.response?.data?.detail || 'Failed to create session';
      setError(errorMsg);
      setSelectedMode(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-light dark:bg-gradient-dark flex items-center justify-center p-4 custom-scrollbar relative overflow-hidden">
      {/* Subtle decorative elements - NO purple/pink in dark mode */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-96 bg-gradient-glow dark:bg-gradient-glow-dark opacity-40 pointer-events-none" />
      <div className="absolute top-10 left-10 w-96 h-96 bg-cyber-blue/5 dark:bg-cyber-blue/10 rounded-full blur-3xl animate-float" />
      <div className="absolute top-40 right-20 w-80 h-80 bg-cyber-cyan/5 dark:bg-cyber-cyan/10 rounded-full blur-3xl animate-float" style={{animationDelay: '2s'}} />
      <div className="absolute bottom-20 left-20 w-72 h-72 bg-cyber-orange/4 dark:bg-cyber-orange/10 rounded-full blur-3xl animate-float" style={{animationDelay: '4s'}} />
      <div className="absolute bottom-40 right-10 w-96 h-96 bg-cyber-cyan/4 dark:bg-cyber-cyan/10 rounded-full blur-3xl animate-float" style={{animationDelay: '6s'}} />
      
      <div className="max-w-7xl w-full relative z-10">
        {/* Theme Toggle and Back Button - Top Right */}
        <div className="absolute top-4 right-4 z-20 flex items-center gap-3">
          <Link
            to="/"
            className="px-4 py-2 text-sm font-semibold text-gray-600 dark:text-dark-text-secondary hover:text-cyber-blue dark:hover:text-cyber-blue transition-colors flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Link>
          <ThemeToggle />
        </div>
        
        {/* Beautiful Header with LINA Title */}
        <div className="text-center mb-12">
          {/* Main LINA Title */}
          <div className="mb-6">
            <h1 className="text-6xl md:text-7xl font-black mb-4 tracking-tight bg-gradient-to-r from-cyber-blue via-cyber-cyan to-cyber-orange bg-clip-text text-transparent">
              Choose Your Mode
            </h1>
            <div className="h-1.5 w-40 mx-auto rounded-full bg-gradient-to-r from-cyber-blue via-cyber-cyan to-cyber-orange" />
          </div>
          
          {/* Subtitle */}
          <div className="max-w-2xl mx-auto">
            <p className="text-xl md:text-2xl font-bold text-gray-800 dark:text-dark-text mb-2">
              Select your preferred interaction mode
            </p>
            <p className="text-gray-600 dark:text-dark-text-secondary">
              Each mode offers a different experience tailored to your needs
            </p>
          </div>
        </div>

        {/* Enhanced Mode Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {modes.map((mode, index) => {
            const isSelected = selectedMode === mode.id;
            const colors = [
              { 
                primary: '#3B82F6', 
                secondary: '#60A5FA', 
                light: 'rgba(59, 130, 246, 0.1)',
                glow: 'rgba(59, 130, 246, 0.3)'
              },
              { 
                primary: '#06B6D4', 
                secondary: '#22D3EE', 
                light: 'rgba(6, 182, 212, 0.1)',
                glow: 'rgba(6, 182, 212, 0.3)'
              },
              { 
                primary: '#F59E0B', 
                secondary: '#FBBF24', 
                light: 'rgba(249, 115, 22, 0.1)',
                glow: 'rgba(249, 115, 22, 0.3)'
              }
            ];
            const colorScheme = colors[index];
            
            return (
              <button
                key={mode.id}
                onClick={() => handleSelectMode(mode.id)}
                disabled={isLoading || selectedMode !== null}
                className="group relative"
              >
                {/* Glow effect on hover */}
                <div 
                  className={`absolute -inset-1 rounded-3xl blur-xl transition-opacity duration-500 ${
                    isSelected ? 'opacity-100' : 'opacity-0 group-hover:opacity-50'
                  }`}
                  style={{
                    background: `linear-gradient(135deg, ${colorScheme.primary}, ${colorScheme.secondary})`,
                  }}
                />
                
                <div 
                  className={`
                    relative
                    p-10
                    rounded-3xl
                    transform
                    transition-all
                    duration-500
                    flex
                    flex-col
                    items-center
                    text-center
                    space-y-6
                    bg-white
                    dark:bg-dark-bg-secondary
                    ${isSelected 
                      ? `shadow-2xl scale-105` 
                      : 'shadow-lg hover:shadow-2xl hover:scale-[1.02] hover:-translate-y-2'}
                    ${!isSelected ? 'border-2 border-light-border dark:border-dark-border' : ''}
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                    disabled:transform-none
                    disabled:hover:shadow-lg
                  `}
                  style={{
                    borderColor: isSelected ? colorScheme.primary : undefined,
                    borderWidth: isSelected ? '3px' : undefined,
                  }}
                >
                  {/* Animated top gradient accent */}
                  <div 
                    className={`absolute top-0 left-0 right-0 h-1.5 rounded-t-3xl transition-all duration-500 ${
                      isSelected ? 'opacity-100 h-2' : 'opacity-0 group-hover:opacity-100 h-1.5'
                    }`}
                    style={{
                      background: `linear-gradient(90deg, ${colorScheme.primary}, ${colorScheme.secondary}, ${colorScheme.primary})`,
                      backgroundSize: '200% 100%',
                      animation: isSelected ? 'gradient 3s linear infinite' : 'none',
                    }}
                  />
                  
                  {/* Enhanced Icon with gradient background */}
                  <div 
                    className={`
                      p-6 
                      rounded-2xl 
                      transition-all 
                      duration-500
                      ${isSelected ? 'scale-110 shadow-lg' : 'group-hover:scale-105'}
                      relative
                      overflow-hidden
                    `}
                    style={{
                      background: isSelected 
                        ? `linear-gradient(135deg, ${colorScheme.primary}, ${colorScheme.secondary})`
                        : `linear-gradient(135deg, ${colorScheme.light}, ${colorScheme.light})`,
                      color: isSelected ? '#FFFFFF' : colorScheme.primary,
                    }}
                  >
                    {/* Icon glow effect */}
                    {isSelected && (
                      <div 
                        className="absolute inset-0 rounded-2xl opacity-50 animate-pulse"
                        style={{
                          background: `radial-gradient(circle, ${colorScheme.glow}, transparent)`,
                        }}
                      />
                    )}
                    <div className="relative z-10">
                      {mode.icon}
                    </div>
                  </div>
                  
                  {/* Title with better typography */}
                  <h2 
                    className={`text-2xl font-black transition-colors duration-300 ${
                      isSelected ? '' : 'text-gray-900 dark:text-dark-text'
                    }`}
                    style={{
                      color: isSelected ? colorScheme.primary : undefined,
                    }}
                  >
                    {mode.name}
                  </h2>
                  
                  {/* Short description */}
                  <p className="text-base font-semibold text-gray-700 dark:text-dark-text-secondary">
                    {mode.description}
                  </p>
                  
                  {/* Detailed description */}
                  <p className="text-sm text-gray-600 dark:text-dark-text-muted leading-relaxed max-w-xs">
                    {mode.detailedDescription}
                  </p>
                  
                  {/* Loading spinner */}
                  {isLoading && selectedMode === mode.id && (
                    <div className="mt-2">
                      <div 
                        className="animate-spin rounded-full h-8 w-8 border-4 border-t-transparent" 
                        style={{ 
                          borderColor: `${colorScheme.primary} ${colorScheme.light} ${colorScheme.light} ${colorScheme.light}` 
                        }}
                      />
                    </div>
                  )}
                  
                  {/* Selected badge with animation */}
                  {isSelected && !isLoading && (
                    <div 
                      className="px-6 py-2 rounded-full text-sm font-bold animate-pulse"
                      style={{
                        background: `linear-gradient(135deg, ${colorScheme.light}, ${colorScheme.light})`,
                        color: colorScheme.primary,
                        boxShadow: `0 0 20px ${colorScheme.glow}`,
                      }}
                    >
                      ✓ Selected
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border-2 border-red-500 dark:border-red-500/30 text-red-700 dark:text-red-400 px-6 py-4 rounded-xl text-center">
            <p className="font-bold">{error}</p>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12">
          <p className="text-gray-600 dark:text-dark-text-secondary text-base">
            Powered by <span className="font-semibold text-cyber-blue">Google Gemini AI</span> • <span className="font-semibold text-cyber-cyan dark:text-cyber-cyan">Phoenix Architecture</span>
          </p>
        </div>
      </div>
    </div>
  );
}

