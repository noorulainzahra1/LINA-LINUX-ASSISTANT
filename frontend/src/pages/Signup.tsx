/**
 * Signup Page
 * User registration form
 */
import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ThemeToggle from '../components/ThemeToggle';

export default function Signup() {
  const navigate = useNavigate();
  const { signup, isAuthenticated, isLoading: authLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      navigate('/model-selection');
    }
  }, [isAuthenticated, authLoading, navigate]);

  const validateForm = (): string | null => {
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'Please enter a valid email address';
    }

    // Username validation
    if (username.length < 3) {
      return 'Username must be at least 3 characters long';
    }
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return 'Username can only contain letters, numbers, and underscores';
    }

    // Password validation
    if (password.length < 6) {
      return 'Password must be at least 6 characters long';
    }

    // Password match validation
    if (password !== confirmPassword) {
      return 'Passwords do not match';
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate form
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      await signup(email, username, password);
      navigate('/model-selection');
    } catch (err: any) {
      setError(err.message || 'Signup failed. Please try again.');
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

        {/* Signup Card */}
        <div className="cyber-card">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-black mb-2 bg-gradient-to-r from-cyber-blue via-cyber-cyan to-cyber-orange bg-clip-text text-transparent">
              Create Account
            </h1>
            <p className="text-gray-600 dark:text-dark-text-secondary">
              Join LINA and start your cybersecurity journey
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-700 dark:text-dark-text mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="cyber-input w-full"
                placeholder="Enter your email"
                disabled={isSubmitting}
              />
            </div>

            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-semibold text-gray-700 dark:text-dark-text mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="cyber-input w-full"
                placeholder="Choose a username"
                disabled={isSubmitting}
                pattern="[a-zA-Z0-9_]+"
              />
              <p className="text-xs text-gray-500 dark:text-dark-text-muted mt-1">
                Letters, numbers, and underscores only
              </p>
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
                placeholder="Create a password"
                disabled={isSubmitting}
                minLength={6}
              />
              <p className="text-xs text-gray-500 dark:text-dark-text-muted mt-1">
                At least 6 characters
              </p>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-semibold text-gray-700 dark:text-dark-text mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="cyber-input w-full"
                placeholder="Confirm your password"
                disabled={isSubmitting}
                minLength={6}
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
                  Creating account...
                </span>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600 dark:text-dark-text-secondary">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-cyber-blue hover:text-cyber-blue-deep font-semibold transition-colors"
              >
                Login
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

