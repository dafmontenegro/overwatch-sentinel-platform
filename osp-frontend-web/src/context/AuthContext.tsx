import React, { createContext, useReducer, useEffect } from 'react';
import type { AuthState, User } from '../types/auth.types';

type AuthAction = 
  | { type: 'LOGIN_SUCCESS', payload: { user: User, token: string } }
  | { type: 'LOGOUT' };

interface AuthContextType extends AuthState {
  loginWithProvider: (provider: string) => Promise<void>;
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
      return { 
        ...state, 
        user: action.payload.user, 
        token: action.payload.token, 
        isAuthenticated: true, 
        loading: false, 
        error: null 
      };
    case 'LOGOUT':
      return { 
        ...state, 
        user: null, 
        token: null, 
        isAuthenticated: false, 
        loading: false, 
        error: null 
      };
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

  const loginWithProvider = async () => {
    // Simulación de usuario autenticado
    const mockUser: User = {
      id: 'user-123',
      name: 'Usuario Demo',
      email: 'demo@osp-sentinel.com',
      role: 'user',
      cameras: ['cam-1', 'cam-2']
    };
    
    // Simular token JWT
    const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsIm5hbWUiOiJVc3VhcmlvIERlbW8iLCJpYXQiOjE2MTYyMzkwMjJ9';
    
    // Guardar en localStorage para persistencia
    localStorage.setItem('user', JSON.stringify(mockUser));
    localStorage.setItem('token', mockToken);
    
    dispatch({ 
      type: 'LOGIN_SUCCESS', 
      payload: { user: mockUser, token: mockToken } 
    });
  };

  const logout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    dispatch({ type: 'LOGOUT' });
  };

  // Verificar si hay sesión guardada al cargar
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const savedToken = localStorage.getItem('token');
    
    if (savedUser && savedToken) {
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: JSON.parse(savedUser),
          token: savedToken
        }
      });
    }
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, loginWithProvider, logout }}>
      {children}
    </AuthContext.Provider>
  );
};