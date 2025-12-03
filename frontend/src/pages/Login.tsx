/**
 * Login Page
 * User authentication form
 */
import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ThemeToggle from '../components/ThemeToggle';

export default function Login() {
  const navigate = useNavigate();
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      navigate('/model-selection');
    }
  }, [isAuthenticated, authLoading, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate('/model-selection');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-light dark:bg-gradient-dark flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-blue mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-dark-text-secondary">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-light dark:bg-gradient-dark flex items-center justify-center p-4 custom-scrollbar relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-96 bg-gradient-glow dark:bg-gradient-glow-dark opacity-40 pointer-events-none" />
      <div className="absolute top-10 left-10 w-96 h-96 bg-cyber-blue/5 dark:bg-cyber-blue/10 rounded-full blur-3xl animate-float" />
      <div className="absolute top-40 right-20 w-80 h-80 bg-cyber-cyan/5 dark:bg-cyber-cyan/10 rounded-full blur-3xl animate-float" style={{animationDelay: '2s'}} />

      <div className="max-w-md w-full relative z-10">
        {/* Theme Toggle - Top Right */}
        <div className="absolute -top-16 right-0 z-20">
          <ThemeToggle />
        </div>

        {/* Login Card */}
        <div className="cyber-card">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-black mb-2 bg-gradient-to-r from-cyber-blue via-cyber-cyan to-cyber-orange bg-clip-text text-transparent">
              Welcome Back
            </h1>
            <p className="text-gray-600 dark:text-dark-text-secondary">
              Sign in to continue to LINA
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email/Username Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-700 dark:text-dark-text mb-2">
                Email or Username
              </label>
              <input
                id="email"
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="cyber-input w-full"
                placeholder="Enter your email or username"
                disabled={isSubmitting}
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-700 dark:text-dark-text mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="cyber-input w-full"
                placeholder="Enter your password"
                disabled={isSubmitting}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border-2 border-red-500 dark:border-red-500/30 text-red-700 dark:text-red-400 px-4 py-3 rounded-xl">
                <p className="font-semibold text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="cyber-button w-full py-3 text-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Logging in...
                </span>
              ) : (
                'Login'
              )}
            </button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600 dark:text-dark-text-secondary">
              Don't have an account?{' '}
              <Link
                to="/signup"
                className="text-cyber-blue hover:text-cyber-blue-deep font-semibold transition-colors"
              >
                Sign up
              </Link>
            </p>
          </div>

          {/* Back to Landing */}
          <div className="mt-4 text-center">
            <Link
              to="/"
              className="text-sm text-gray-500 dark:text-dark-text-muted hover:text-cyber-blue transition-colors"
            >
              ← Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

