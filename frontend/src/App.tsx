/**
 * Main App component
 */
import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import { SessionProvider } from './contexts/SessionContext';
import { ThemeProvider } from './contexts/ThemeContext';
import StartupAnimation from './components/StartupAnimation';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ModeSelection from './pages/ModeSelection';
import Dashboard from './pages/Dashboard';
import MainChat from './pages/MainChat';
import Analytics from './pages/Analytics';
import Tools from './pages/Tools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const [showStartup, setShowStartup] = useState(true);

  useEffect(() => {
    // Check if we've shown the startup animation before (stored in sessionStorage)
    const hasSeenStartup = sessionStorage.getItem('lina_startup_seen');
    if (hasSeenStartup) {
      setShowStartup(false);
    } else {
      // Mark as seen after a delay (will be set when animation completes)
      sessionStorage.setItem('lina_startup_seen', 'true');
    }
  }, []);

  const handleAnimationComplete = () => {
    setShowStartup(false);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <SessionProvider>
            <BrowserRouter>
              {showStartup && <StartupAnimation onComplete={handleAnimationComplete} />}
              {!showStartup && (
                <Routes>
                  {/* Public routes */}
                  <Route path="/" element={<Landing />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/signup" element={<Signup />} />
                  
                  {/* Protected routes */}
                  <Route
                    path="/model-selection"
                    element={
                      <ProtectedRoute>
                        <ModeSelection />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <Dashboard />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/chat"
                    element={
                      <ProtectedRoute>
                        <MainChat />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/analytics"
                    element={
                      <ProtectedRoute>
                        <Analytics />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/tools"
                    element={
                      <ProtectedRoute>
                        <Tools />
                      </ProtectedRoute>
                    }
                  />
                  
                  {/* Catch all - redirect to landing */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              )}
            </BrowserRouter>
          </SessionProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

