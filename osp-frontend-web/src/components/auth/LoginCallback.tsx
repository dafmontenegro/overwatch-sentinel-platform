import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import AuthLayout from '../../layouts/AuthLayout';

interface LoginCallbackProps {
  onComplete?: () => void;
}

const LoginCallback: React.FC<LoginCallbackProps> = ({ onComplete }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginWithProvider, clearError } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [errorMessage, setErrorMessage] = useState<string>('');

  useEffect(() => {
    const processCallback = async () => {
      try {
        const params = new URLSearchParams(location.search);
        const accessToken = params.get('access_token');
        const authError = params.get('error');

        // Limpiar errores previos
        clearError();

        if (authError) {
          throw new Error(getErrorMessage(authError));
        }

        if (!accessToken) {
          throw new Error('No se recibió token de autenticación');
        }

        // Procesar el token
        await loginWithProvider(accessToken);
        setStatus('success');

        // Esperar un momento para mostrar el éxito antes de redirigir
        setTimeout(() => {
          navigate('/live', { replace: true });
          onComplete?.();
        }, 1500);

      } catch (error) {
        console.error('Error en callback de autenticación:', error);
        setStatus('error');
        setErrorMessage(error instanceof Error ? error.message : 'Error desconocido');

        // Redirigir al login después de mostrar el error
        setTimeout(() => {
          navigate('/login', { replace: true });
          onComplete?.();
        }, 3000);
      }
    };

    processCallback();
  }, [location, loginWithProvider, navigate, clearError, onComplete]);

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

  const getStatusConfig = () => {
    switch (status) {
      case 'processing':
        return {
          color: 'border-capri',
          bgColor: 'bg-capri/10',
          textColor: 'text-capri',
          message: 'Procesando autenticación...',
          submessage: 'Validando credenciales y configurando tu sesión',
          icon: (
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-capri mx-auto mb-4"></div>
          )
        };
      case 'success':
        return {
          color: 'border-green-500',
          bgColor: 'bg-green-50',
          textColor: 'text-green-700',
          message: '¡Autenticación exitosa!',
          submessage: 'Redirigiendo al dashboard...',
          icon: (
            <div className="mx-auto mb-4 w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )
        };
      case 'error':
        return {
          color: 'border-red-500',
          bgColor: 'bg-red-50',
          textColor: 'text-red-700',
          message: 'Error de autenticación',
          submessage: errorMessage || 'Redirigiendo al login...',
          icon: (
            <div className="mx-auto mb-4 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          )
        };
    }
  };

  const config = getStatusConfig();

  return (
    <AuthLayout>
      <div className={`text-center py-8 px-6 rounded-lg border-2 ${config.color} ${config.bgColor}`}>
        {config.icon}
        
        <h2 className={`text-xl font-bold ${config.textColor} mb-2`}>
          {config.message}
        </h2>
        
        <p className={`text-sm ${config.textColor} mb-4`}>
          {config.submessage}
        </p>

        {status === 'processing' && (
          <div className="mt-6">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-capri h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="mt-6">
            <button
              onClick={() => navigate('/login', { replace: true })}
              className="px-4 py-2 bg-capri text-white rounded-lg hover:bg-capridark transition duration-200"
            >
              Volver al login
            </button>
          </div>
        )}
      </div>
    </AuthLayout>
  );
};

export default LoginCallback;