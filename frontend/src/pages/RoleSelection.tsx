/**
 * Role Selection Page
 * First screen users see - allows them to select their role
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../contexts/SessionContext';
import { UserRole } from '../types';
import { GraduationCap, Search, Shield } from 'lucide-react';
import ThemeToggle from '../components/ThemeToggle';

const roles: Array<{
  id: UserRole;
  emoji: string;
  icon: React.ReactNode;
  name: string;
  description: string;
  color: string;
}> = [
  {
    id: 'Student',
    emoji: '🎓',
    icon: <GraduationCap className="w-12 h-12" />,
    name: 'Student',
    description: 'Learning cybersecurity, need explanations and guidance',
    color: 'bg-green-500 hover:bg-green-600',
  },
  {
    id: 'Forensic Expert',
    emoji: '🔍',
    icon: <Search className="w-12 h-12" />,
    name: 'Forensic Expert',
    description: 'Digital forensics, memory analysis, incident response',
    color: 'bg-red-500 hover:bg-red-600',
  },
  {
    id: 'Penetration Tester',
    emoji: '🛡️',
    icon: <Shield className="w-12 h-12" />,
    name: 'Penetration Tester',
    description: 'Offensive security, vulnerability assessment, red team',
    color: 'bg-cyan-500 hover:bg-cyan-600 dark:bg-cyan-600 dark:hover:bg-cyan-700',
  },
];

export default function RoleSelection() {
  const navigate = useNavigate();
  const { createSession, isLoading } = useSession();
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelectRole = async (role: UserRole) => {
    setSelectedRole(role);
    setError(null);

    try {
      await createSession(role);
      navigate('/chat');
    } catch (err: any) {
      setError(err.message || 'Failed to create session');
      setSelectedRole(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 dark:from-dark-bg dark:via-dark-bg-alt dark:to-dark-bg flex items-center justify-center p-4 relative">
      {/* Theme Toggle - Top Right */}
      <div className="absolute top-4 right-4 z-20">
        <ThemeToggle />
      </div>
      
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            <span className="text-cyan-400">L</span>
            <span className="text-cyan-300">I</span>
            <span className="text-cyan-400">N</span>
            <span className="text-cyan-300">A</span>
          </h1>
          <p className="text-xl text-gray-300 dark:text-dark-text mb-2">
            AI-Powered Cybersecurity Assistant
          </p>
          <p className="text-gray-400 dark:text-dark-text-secondary">
            Select your role to begin
          </p>
        </div>

        {/* Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {roles.map((role) => (
            <button
              key={role.id}
              onClick={() => handleSelectRole(role.id)}
              disabled={isLoading || selectedRole !== null}
              className={`
                ${role.color}
                text-white
                p-8
                rounded-xl
                shadow-2xl
                transform
                transition-all
                duration-300
                hover:scale-105
                hover:shadow-cyan-500/50
                disabled:opacity-50
                disabled:cursor-not-allowed
                disabled:transform-none
                flex
                flex-col
                items-center
                space-y-4
              `}
            >
              <div className="text-6xl mb-2">{role.emoji}</div>
              <h2 className="text-2xl font-bold">{role.name}</h2>
              <p className="text-center text-sm opacity-90">{role.description}</p>
              {isLoading && selectedRole === role.id && (
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              )}
            </button>
          ))}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/20 dark:bg-red-900/20 border border-red-500 dark:border-red-500/50 text-red-200 dark:text-red-400 px-4 py-3 rounded-lg text-center">
            {error}
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-gray-400 dark:text-dark-text-secondary text-sm mt-8">
          <p>Powered by Google Gemini AI • Phoenix Architecture</p>
        </div>
      </div>
    </div>
  );
}

