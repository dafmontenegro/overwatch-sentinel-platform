import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './useAuth';

interface UseLoginCallbackReturn {
  status: 'processing' | 'success' | 'error';
  errorMessage: string;
  isCallbackRoute: boolean;
}

export const useLoginCallback = (): UseLoginCallbackReturn => {
  const location = useLocation();
  const navigate = useNavigate();
  const { loginWithProvider, clearError } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const params = new URLSearchParams(location.search);
  const isCallbackRoute = params.has('access_token') || params.has('error');

  useEffect(() => {
    if (!isCallbackRoute) return;

    const processCallback = async () => {
      try {
        const accessToken = params.get('access_token');
        const authError = params.get('error');

        clearError();

        if (authError) {
          throw new Error(`Error de autenticación: ${authError}`);
        }

        if (!accessToken) {
          throw new Error('No se recibió token de autenticación');
        }

        await loginWithProvider(accessToken);
        setStatus('success');

        setTimeout(() => {
          navigate('/live', { replace: true });
        }, 1500);

      } catch (error) {
        setStatus('error');
        setErrorMessage(error instanceof Error ? error.message : 'Error desconocido');

        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 3000);
      }
    };

    processCallback();
  }, [isCallbackRoute, params, loginWithProvider, navigate, clearError]);

  return {
    status,
    errorMessage,
    isCallbackRoute
  };
};