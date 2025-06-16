import React, { createContext, useReducer, useEffect } from 'react';
import type { AuthState, User } from '../types/auth.types';
import { fetchUserId } from '../services/authService';

type AuthAction =
  | { type: 'LOGIN_SUCCESS', payload: { user: User, token: string } }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING', payload: boolean }
  | { type: 'SET_ERROR', payload: string | null };

interface AuthContextType extends AuthState {
  loginWithProvider: (token: string) => Promise<void>;
  logout: () => void;
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,
  error: null
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return { ...state, user: action.payload.user, token: action.payload.token, isAuthenticated: true, loading: false, error: null };
    case 'LOGOUT':
      return { ...initialState };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
};

export const AuthContext = createContext<AuthContextType>({
  ...initialState,
  loginWithProvider: async () => {},
  logout: () => {}
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const loginWithProvider = async (token: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      // Obtén el user_id del endpoint protegido
      const userId = await fetchUserId(token);

      // Construye el objeto User básico
      const user: User = {
        id: userId,
        name: '', // No disponible por ahora
        email: '', // No disponible por ahora
        role: 'user',
        cameras: []
      };

      localStorage.setItem('user', JSON.stringify(user));
      dispatch({ type: 'LOGIN_SUCCESS', payload: { user, token } });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Error de autenticación' });
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      throw error; // Re-lanzar para que LoginCallbackPage pueda manejarlo
    }
  };


  const logout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    dispatch({ type: 'LOGOUT' });
  };

  // Al cargar, verifica si hay sesión guardada
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (savedToken && savedUser) {
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: JSON.parse(savedUser), token: savedToken }
      });
    }
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, loginWithProvider, logout }}>
      {children}
    </AuthContext.Provider>
  );
};