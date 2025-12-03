/**
 * Session management context for LINA
 */
import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { sessionAPI } from '../services/api';
import type { Session, UserRole, SessionStatus, WorkMode } from '../types';

interface SessionContextType {
  session: Session | null;
  sessionStatus: SessionStatus | null;
  mode: WorkMode | null;
  isLoading: boolean;
  error: string | null;
  createSession: (role: UserRole, mode?: WorkMode) => Promise<void>;
  setMode: (mode: WorkMode) => void;
  refreshStatus: () => Promise<void>;
  clearSession: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [sessionStatus, setSessionStatus] = useState<SessionStatus | null>(null);
  const [mode, setModeState] = useState<WorkMode | null>(() => {
    // Load mode from localStorage
    const savedMode = localStorage.getItem('lina_mode') as WorkMode | null;
    return savedMode || null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setMode = useCallback((newMode: WorkMode) => {
    setModeState(newMode);
    localStorage.setItem('lina_mode', newMode);
    // Update session if it exists
    if (session) {
      setSession({ ...session, mode: newMode });
    }
  }, [session]);

  const refreshStatus = useCallback(async (sessionId?: string) => {
    const id = sessionId || session?.session_id;
    if (!id) return;

    try {
      const status = await sessionAPI.getStatus(id);
      setSessionStatus(status);
    } catch (err: any) {
      console.error('Failed to refresh session status:', err);
      // Don't set error here, just log it
    }
  }, [session?.session_id]);

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSession = localStorage.getItem('lina_session');
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession);
        // Verify session still exists on backend before using it
        sessionAPI.getStatus(parsed.session_id)
          .then(() => {
            setSession(parsed);
            // Restore mode if session has one
            if (parsed.mode) {
              setModeState(parsed.mode);
            }
            // Refresh status after session is set
            setTimeout(() => refreshStatus(parsed.session_id), 100);
          })
          .catch((err) => {
            // Session doesn't exist on backend, clear it
            console.warn('Saved session not found on backend, clearing:', err);
            localStorage.removeItem('lina_session');
            setSession(null);
            // Navigate to role selection if we're on chat page
            if (window.location.pathname !== '/') {
              setTimeout(() => {
                window.location.href = '/';
              }, 100);
            }
          });
      } catch (e) {
        console.error('Failed to load saved session:', e);
        localStorage.removeItem('lina_session');
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-refresh status periodically
  useEffect(() => {
    if (!session?.session_id) return;

    const interval = setInterval(() => {
      refreshStatus();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [session?.session_id, refreshStatus]);

  const createSession = async (role: UserRole, workMode?: WorkMode) => {
    setIsLoading(true);
    setError(null);

    try {
      // Pass mode to backend when creating session
      const newSession = await sessionAPI.create(role, undefined, workMode || mode || 'interactive');
      // Add mode to session
      const sessionWithMode = { ...newSession, mode: workMode || mode || 'interactive' };
      setSession(sessionWithMode);
      
      // Set mode if provided
      if (workMode) {
        setModeState(workMode);
        localStorage.setItem('lina_mode', workMode);
      }
      
      localStorage.setItem('lina_session', JSON.stringify(sessionWithMode));
      
      // Fetch initial status in background (don't block navigation)
      refreshStatus(newSession.session_id).catch(err => {
        console.warn('Failed to refresh status after session creation:', err);
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create session');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const clearSession = () => {
    setSession(null);
    setSessionStatus(null);
    localStorage.removeItem('lina_session');
  };

  return (
    <SessionContext.Provider
      value={{
        session,
        sessionStatus,
        mode,
        isLoading,
        error,
        createSession,
        setMode,
        refreshStatus,
        clearSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}
