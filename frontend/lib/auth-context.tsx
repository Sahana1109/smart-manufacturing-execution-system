"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User } from "@/types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchCurrentUser = async (authToken: string) => {
    try {
      const res = await fetch("/api/v1/auth/me", {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      if (res.ok) {
        const userData: User = await res.json();
        setUser(userData);
      } else {
        // Token invalid or expired
        localStorage.removeItem("smartmes_token");
        setToken(null);
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const storedToken = localStorage.getItem("smartmes_token");
    if (storedToken) {
      setToken(storedToken);
      fetchCurrentUser(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (newToken: string) => {
    localStorage.setItem("smartmes_token", newToken);
    setToken(newToken);
    await fetchCurrentUser(newToken);
  };

  const logout = () => {
    localStorage.removeItem("smartmes_token");
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    if (token) {
      await fetchCurrentUser(token);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
