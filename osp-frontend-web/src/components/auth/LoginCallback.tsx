import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLoginCallback } from '../../hooks/useLoginCallback';
import AuthLayout from '../../layouts/AuthLayout';

interface LoginCallbackProps {
  onComplete?: () => void;
}

const LoginCallback: React.FC<LoginCallbackProps> = ({ onComplete }) => {
  const navigate = useNavigate();
  const { status, errorMessage, retryCallback } = useLoginCallback();

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

  // Llamar onComplete cuando el proceso termine
  React.useEffect(() => {
    if (status === 'success' || status === 'error') {
      onComplete?.();
    }
  }, [status, onComplete]);

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
          <div className="mt-6 space-y-3">
            <button
              onClick={retryCallback}
              className="px-4 py-2 bg-capri text-white rounded-lg hover:bg-capridark transition duration-200 mr-3"
            >
              Reintentar
            </button>
            <button
              onClick={() => navigate('/login', { replace: true })}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition duration-200"
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