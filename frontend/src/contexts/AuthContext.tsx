/**
 * Authentication Context for LINA
 * Manages user authentication using browser storage
 */
import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';

export interface User {
  id: string;
  email: string;
  username: string;
  createdAt: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Simple hash function for passwords (basic implementation for browser storage)
function simpleHash(password: string): string {
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return hash.toString(36);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = () => {
      try {
        const storedUser = localStorage.getItem('lina_current_user');
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error('Failed to load user from localStorage:', error);
        localStorage.removeItem('lina_current_user');
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const usersJson = localStorage.getItem('lina_users');
      const users = usersJson ? JSON.parse(usersJson) : [];
      
      const hashedPassword = simpleHash(password);
      const foundUser = users.find(
        (u: any) => (u.email === email || u.username === email) && u.password === hashedPassword
      );

      if (!foundUser) {
        throw new Error('Invalid email/username or password');
      }

      const userData: User = {
        id: foundUser.id,
        email: foundUser.email,
        username: foundUser.username,
        createdAt: foundUser.createdAt,
      };

      setUser(userData);
      localStorage.setItem('lina_current_user', JSON.stringify(userData));
    } catch (error: any) {
      throw new Error(error.message || 'Login failed');
    }
  }, []);

  const signup = useCallback(async (email: string, username: string, password: string) => {
    try {
      const usersJson = localStorage.getItem('lina_users');
      const users = usersJson ? JSON.parse(usersJson) : [];

      // Check if email or username already exists
      const emailExists = users.some((u: any) => u.email === email);
      const usernameExists = users.some((u: any) => u.username === username);

      if (emailExists) {
        throw new Error('Email already registered');
      }

      if (usernameExists) {
        throw new Error('Username already taken');
      }

      // Create new user
      const newUser = {
        id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        email,
        username,
        password: simpleHash(password),
        createdAt: new Date().toISOString(),
      };

      users.push(newUser);
      localStorage.setItem('lina_users', JSON.stringify(users));

      // Auto-login
      const userData: User = {
        id: newUser.id,
        email: newUser.email,
        username: newUser.username,
        createdAt: newUser.createdAt,
      };

      setUser(userData);
      localStorage.setItem('lina_current_user', JSON.stringify(userData));
    } catch (error: any) {
      throw new Error(error.message || 'Signup failed');
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('lina_current_user');
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

