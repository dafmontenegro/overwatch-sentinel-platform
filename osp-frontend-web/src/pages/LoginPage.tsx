import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useLoginCallback } from '../hooks/useLoginCallback';
import AuthLayout from '../layouts/AuthLayout';
import LoginCallback from '../components/auth/LoginCallback';
import { SiGoogle } from 'react-icons/si'; 
import { FaGithub } from 'react-icons/fa';

const API_URL = import.meta.env.VITE_API_URL;

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { isCallbackRoute } = useLoginCallback();

  // Redirigir si ya está autenticado y no es una ruta de callback
  useEffect(() => {
    if (isAuthenticated && !isCallbackRoute) {
      navigate('/live');
    }
  }, [isAuthenticated, navigate, isCallbackRoute]);

  // Mostrar el componente de callback si estamos en una ruta de callback
  if (isCallbackRoute) {
    return <LoginCallback />;
  }

  const handleFederatedLogin = (provider: 'google' | 'github') => {
    window.location.href = `${API_URL}/auth/${provider}`;
  };

  return (
    <AuthLayout>
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-asphalt">
            Iniciar Sesión
          </h2>
          <p className="mt-2 text-sm text-asphaltlight">
            Accede a tu cuenta para ver tus cámaras de vigilancia
          </p>
        </div>

        <div className="mt-8 space-y-4">
          <button
            onClick={() => handleFederatedLogin('google')}
            className="w-full flex justify-center items-center px-4 py-3 border border-transparent rounded-lg shadow-lg bg-red-600 text-white font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-300 transform hover:scale-105"
          >
            <SiGoogle className="w-5 h-5 mr-3" />
            Continuar con Google
          </button>

          <button
            onClick={() => handleFederatedLogin('github')}
            className="w-full flex justify-center items-center px-4 py-3 border border-asphaltlight rounded-lg shadow-lg bg-asphalt text-white font-medium hover:bg-asphaltdark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-asphaltlight transition-all duration-300 transform hover:scale-105"
          >
            <FaGithub className="w-5 h-5 mr-3" />
            Continuar con GitHub
          </button>
        </div>

        <div className="mt-6">
          <button
            onClick={() => navigate('/')}
            className="w-full text-center text-sm text-asphaltlight hover:text-capri transition duration-200 font-medium"
          >
            ← Volver al inicio
          </button>
        </div>
      </div>
    </AuthLayout>
  );
};

export default LoginPage;