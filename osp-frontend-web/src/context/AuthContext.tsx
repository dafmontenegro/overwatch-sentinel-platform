import React, { createContext, useReducer, useEffect } from 'react';
import type { AuthState, User } from '../types/auth.types';
import { fetchUser, fetchUserId } from '../services/authService';

type AuthAction =
  | { type: 'LOGIN_REQUEST' }
  | { type: 'LOGIN_SUCCESS', payload: { user: User, token: string } }
  | { type: 'LOGIN_FAILURE', payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING', payload: boolean }
  | { type: 'SET_ERROR', payload: string | null }
  | { type: 'CLEAR_ERROR' };

interface AuthContextType extends AuthState {
  loginWithProvider: (token: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
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
    case 'LOGIN_REQUEST':
      return { 
        ...state, 
        loading: true, 
        error: null 
      };
    case 'LOGIN_SUCCESS':
      return { 
        ...state, 
        user: action.payload.user, 
        token: action.payload.token, 
        isAuthenticated: true, 
        loading: false, 
        error: null 
      };
    case 'LOGIN_FAILURE':
      return { 
        ...state, 
        user: null, 
        token: null, 
        isAuthenticated: false, 
        loading: false, 
        error: action.payload 
      };
    case 'LOGOUT':
      return { 
        ...initialState 
      };
    case 'SET_LOADING':
      return { 
        ...state, 
        loading: action.payload 
      };
    case 'SET_ERROR':
      return { 
        ...state, 
        error: action.payload,
        loading: false 
      };
    case 'CLEAR_ERROR':
      return { 
        ...state, 
        error: null 
      };
    default:
      return state;
  }
};

export const AuthContext = createContext<AuthContextType>({
  ...initialState,
  loginWithProvider: async () => {},
  logout: () => {},
  clearError: () => {}
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const loginWithProvider = async (token: string) => {
    dispatch({ type: 'LOGIN_REQUEST' });
    
    try {
      // Validar que el token no esté vacío
      if (!token || token.trim() === '') {
        throw new Error('Token inválido');
      }

      // Obtener el user_id del endpoint protegido
      const userData = await fetchUser(token);
      console.log(userData);

      // Validar que tenemos todos los datos necesarios
      if (!userData.id || !userData.email) {
        throw new Error('Datos de usuario incompletos');
      }

      // Guardar en localStorage DESPUÉS de validar que todo está correcto
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Actualizar estado
      dispatch({ 
        type: 'LOGIN_SUCCESS', 
        payload: { 
          user: userData, 
          token 
        } 
      });

    } catch (error) {
      // Limpiar localStorage en caso de error
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'Error de autenticación';
      
      dispatch({ 
        type: 'LOGIN_FAILURE', 
        payload: errorMessage 
      });
      
      throw error;
    }
  };


  const logout = () => {
    // Limpiar localStorage
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    
    // Actualizar estado
    dispatch({ type: 'LOGOUT' });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Al cargar, verificar si hay sesión guardada
  useEffect(() => {
    // Solo ejecutar en el cliente (evitar problemas de SSR)
    if (typeof window === 'undefined') return;

    try {
      const savedToken = localStorage.getItem('token');
      const savedUser = localStorage.getItem('user');
      
      if (savedToken && savedUser) {
        // Validar que el JSON del usuario sea válido
        const parsedUser = JSON.parse(savedUser);
        
        // Verificar que el usuario tenga las propiedades necesarias
        if (parsedUser && parsedUser.id) {
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: { 
              user: parsedUser, 
              token: savedToken 
            }
          });
        } else {
          // Si los datos están corruptos, limpiar
          localStorage.removeItem('user');
          localStorage.removeItem('token');
        }
      }
    } catch (error) {
      // Si hay error al parsear, limpiar localStorage
      console.error('Error al cargar sesión guardada:', error);
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
  }, []);

  // Validar token periódicamente (opcional)
  useEffect(() => {
    if (!state.token || !state.isAuthenticated) return;

    const validateToken = async () => {
      try {
        await fetchUserId(state.token!);
      } catch (error) {
        // Si el token es inválido, hacer logout
        console.warn('Token inválido, cerrando sesión');
        logout();
      }
    };

    // Validar token cada 30 minutos
    const interval = setInterval(validateToken, 30 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [state.token, state.isAuthenticated]);

  return (
    <AuthContext.Provider value={{ 
      ...state, 
      loginWithProvider, 
      logout, 
      clearError 
    }}>
      {children}
    </AuthContext.Provider>
  );
};