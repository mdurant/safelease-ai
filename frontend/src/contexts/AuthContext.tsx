import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { authApi, type Tokens, type User } from "../api/auth";

interface AuthState {
  user: User | null;
  access: string | null;
  refresh: string | null;
  loading: boolean;
}

const AuthContext = createContext<{
  state: AuthState;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setTokens: (t: Tokens) => void;
  refreshUser: () => Promise<void>;
  getAccessToken: () => string | null;
} | null>(null);

const ACCESS_KEY = "safelease_access";
const REFRESH_KEY = "safelease_refresh";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    access: localStorage.getItem(ACCESS_KEY),
    refresh: localStorage.getItem(REFRESH_KEY),
    loading: true,
  });

  const getAccessToken = useCallback(() => state.access || localStorage.getItem(ACCESS_KEY), [state.access]);

  const persistTokens = useCallback((access: string, refresh: string) => {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
    setState((s) => ({ ...s, access, refresh }));
  }, []);

  const clearTokens = useCallback(() => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setState((s) => ({ ...s, access: null, refresh: null, user: null }));
  }, []);

  const refreshAccess = useCallback(async (): Promise<string | null> => {
    const refresh = state.refresh || localStorage.getItem(REFRESH_KEY);
    if (!refresh) return null;
    try {
      const data = await authApi.refreshToken(refresh);
      persistTokens(data.access, refresh);
      return data.access;
    } catch {
      clearTokens();
      return null;
    }
  }, [state.refresh, persistTokens, clearTokens]);

  const refreshUser = useCallback(async () => {
    const access = getAccessToken();
    if (!access) return;
    try {
      const user = await authApi.me(access);
      setState((s) => ({ ...s, user }));
    } catch {
      const newAccess = await refreshAccess();
      if (newAccess) {
        const user = await authApi.me(newAccess);
        setState((s) => ({ ...s, user }));
      }
    }
  }, [getAccessToken, refreshAccess]);

  useEffect(() => {
    if (!state.access && state.refresh) {
      refreshAccess().then(() => setState((s) => ({ ...s, loading: false })));
      return;
    }
    if (!state.access) {
      setState((s) => ({ ...s, loading: false }));
      return;
    }
    authApi
      .me(state.access)
      .then((user) => setState((s) => ({ ...s, user, loading: false })))
      .catch(() => {
        refreshAccess().then((access) => {
          if (access) {
            authApi.me(access).then((user) =>
              setState((s) => ({ ...s, user, loading: false }))
            );
          } else {
            setState((s) => ({ ...s, loading: false }));
          }
        });
      });
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const tokens = await authApi.login(email, password);
      persistTokens(tokens.access, tokens.refresh);
      const user = await authApi.me(tokens.access);
      setState((s) => ({ ...s, access: tokens.access, refresh: tokens.refresh, user }));
    },
    [persistTokens]
  );

  const logout = useCallback(() => {
    clearTokens();
  }, [clearTokens]);

  const setTokens = useCallback(
    (t: Tokens) => {
      persistTokens(t.access, t.refresh);
      setState((s) => ({ ...s, user: null }));
      authApi.me(t.access).then((user) => setState((s) => ({ ...s, user })));
    },
    [persistTokens]
  );

  const value = useMemo(
    () => ({
      state,
      login,
      logout,
      setTokens,
      refreshUser,
      getAccessToken,
    }),
    [state, login, logout, setTokens, refreshUser, getAccessToken]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
