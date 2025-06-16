import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const LoginCallbackPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginWithProvider } = useAuth();
  const [isClient, setIsClient] = useState(false);
  const [status, setStatus] = useState<'loading' | 'processing' | 'error'>('loading');

  // Asegurar que el componente se renderice igual en servidor y cliente
  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient) return; // Solo ejecutar en el cliente

    const params = new URLSearchParams(location.search);
    const token = params.get('token');
    const error = params.get('error');

    if (token) {
      setStatus('processing');
      // Guardar token y autenticar usuario
      localStorage.setItem('token', token);
      loginWithProvider(token)
        .then(() => {
          navigate('/live');
        })
        .catch((err) => {
          console.error('Error en autenticación:', err);
          setStatus('error');
          // Redirigir a login con error después de 3 segundos
          setTimeout(() => {
            navigate('/login?error=invalid_token');
          }, 3000);
        });
    } else if (error) {
      setStatus('error');
      // Manejar error de autenticación
      setTimeout(() => {
        navigate('/login?error=' + error);
      }, 3000);
    } else {
      // No hay token ni error, redirigir al home
      navigate('/');
    }
  }, [isClient, location, navigate, loginWithProvider]);

  const getStatusMessage = () => {
    if (!isClient) return 'Cargando...';
    
    switch (status) {
      case 'loading':
        return 'Inicializando...';
      case 'processing':
        return 'Procesando autenticación...';
      case 'error':
        return 'Error en la autenticación. Redirigiendo...';
      default:
        return 'Cargando...';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'error':
        return 'border-red-600';
      case 'processing':
        return 'border-green-600';
      default:
        return 'border-blue-600';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-xl text-center max-w-md w-full mx-4">
        {/* Logo */}
        <div className="mx-auto h-16 w-16 bg-gradient-to-r from-capri to-capridark rounded-lg flex items-center justify-center shadow-lg mb-6">
          <svg 
            className="h-10 w-10 text-white" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" 
            />
          </svg>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          <span className="text-capri">OSP</span> Sentinel
        </h2>

        {/* Spinner */}
        <div className={`animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 ${getStatusColor()} mx-auto mb-4`}></div>
        
        {/* Status message */}
        <p className="text-gray-600 mb-2">
          {getStatusMessage()}
        </p>

        {/* Error message adicional */}
        {status === 'error' && (
          <p className="text-sm text-red-600">
            Serás redirigido a la página de login en unos segundos...
          </p>
        )}

        {/* Processing message adicional */}
        {status === 'processing' && (
          <p className="text-sm text-green-600">
            Configurando tu sesión...
          </p>
        )}
      </div>
    </div>
  );
};

export default LoginCallbackPage;