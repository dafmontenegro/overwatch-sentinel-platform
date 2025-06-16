// src/pages/LoginCallbackPage.tsx
import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const LoginCallbackPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginWithProvider } = useAuth();
  const [isClient, setIsClient] = useState(false);

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
      // Guardar token y autenticar usuario
      localStorage.setItem('token', token);
      loginWithProvider(token).then(() => {
        navigate('/live');
      }).catch(() => {
        navigate('/?error=invalid_token');
      });
    } else if (error) {
      // Manejar error de autenticación
      navigate('/?error=' + error);
    } else {
      // No hay token ni error, redirigir al home
      navigate('/');
    }
  }, [isClient, location, navigate, loginWithProvider]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">
          {isClient ? 'Procesando autenticación...' : 'Cargando...'}
        </p>
      </div>
    </div>
  );
};

export default LoginCallbackPage;