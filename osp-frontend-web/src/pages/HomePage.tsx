import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Hero from '../components/home/Hero';
import AboutUs from '../components/home/AboutUs';
import Features from '../components/home/Features';
import ContactSection from '../components/home/ContactSection';
import { useAuth } from '../hooks/useAuth';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Verificar si hay errores en los parámetros de la URL
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const error = params.get('error');
    
    if (error) {
      switch (error) {
        case 'invalid_token':
          setErrorMessage('Token de autenticación inválido. Por favor, intenta de nuevo.');
          break;
        case 'auth_failed':
          setErrorMessage('Error en la autenticación. Por favor, intenta de nuevo.');
          break;
        default:
          setErrorMessage('Ocurrió un error durante la autenticación.');
      }
      
      // Limpiar el error después de 5 segundos
      setTimeout(() => {
        setErrorMessage(null);
        // Limpiar la URL
        navigate('/', { replace: true });
      }, 5000);
    }
  }, [location, navigate]);

  const handleAccess = () => {
    if (isAuthenticated) {
      navigate('/live');
    } else {
      navigate('/login');
    }
  };

  return (
    <MainLayout>
      {/* Mensaje de error */}
      {errorMessage && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mx-4 mt-4">
          <div className="flex">
            <div className="py-1">
              <svg className="fill-current h-6 w-6 text-red-500 mr-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                <path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM9 11V9h2v6H9v-4zm0-6h2v2H9V5z"/>
              </svg>
            </div>
            <div>
              <p className="font-bold">Error de autenticación</p>
              <p className="text-sm">{errorMessage}</p>
            </div>
          </div>
        </div>
      )}

      <Hero 
        title="OSP - Overwatch Sentinel Platform" 
        subtitle="Vigilancia inteligente basada en visión por computadora" 
        ctaText={isAuthenticated ? "Ir al Dashboard" : "Iniciar Sesión"} 
        onCtaClick={handleAccess} 
      />
      <AboutUs />
      <Features />
      <ContactSection />
    </MainLayout>
  );
};

export default HomePage;