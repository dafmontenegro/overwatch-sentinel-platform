import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './useAuth';

interface UseLoginCallbackReturn {
  status: 'processing' | 'success' | 'error';
  errorMessage: string;
  isCallbackRoute: boolean;
  retryCallback: () => void;
}

export const useLoginCallback = (): UseLoginCallbackReturn => {
  const location = useLocation();
  const navigate = useNavigate();
  const { loginWithProvider, clearError } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const params = new URLSearchParams(location.search);
  const isCallbackRoute = params.has('access_token') || params.has('error');

  const getErrorMessage = (error: string): string => {
    const errorMessages: Record<string, string> = {
      'access_denied': 'Acceso denegado. Has cancelado la autenticación.',
      'invalid_request': 'Solicitud inválida. Intenta de nuevo.',
      'unauthorized_client': 'Cliente no autorizado.',
      'unsupported_response_type': 'Tipo de respuesta no soportado.',
      'invalid_scope': 'Alcance inválido.',
      'server_error': 'Error del servidor. Intenta más tarde.',
      'temporarily_unavailable': 'Servicio temporalmente no disponible.',
    };
    return errorMessages[error] || `Error de autenticación: ${error}`;
  };

  const processCallback = async () => {
    if (!isCallbackRoute) return;

    try {
      setStatus('processing');
      const accessToken = params.get('access_token');
      const authError = params.get('error');

      clearError();

      if (authError) {
        throw new Error(getErrorMessage(authError));
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
      console.error('Error en callback de autenticación:', error);
      setStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Error desconocido');

      setTimeout(() => {
        navigate('/login', { replace: true });
      }, 3000);
    }
  };

  const retryCallback = () => {
    processCallback();
  };

  useEffect(() => {
    processCallback();
  }, [isCallbackRoute, location.search]);

  return {
    status,
    errorMessage,
    isCallbackRoute,
    retryCallback
  };
};