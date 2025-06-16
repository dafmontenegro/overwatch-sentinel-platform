import React from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Hero from '../components/home/Hero';
import AboutUs from '../components/home/AboutUs';
import Features from '../components/home/Features';
import ContactSection from '../components/home/ContactSection';
import { useAuth } from '../hooks/useAuth';
import FederatedLogin from '../components/auth/FederatedLogin';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, loginWithProvider } = useAuth();

  const handleAccess = async () => {
    if (isAuthenticated) {
      navigate('/live');
    }
  };

  return (
    <MainLayout>
      <Hero 
        title="OSP - Overwatch Sentinel Platform" 
        subtitle="Vigilancia inteligente basada en visión por computadora" 
        ctaText="Acceder al Sistema" 
        onCtaClick={handleAccess} 
      />
      {/* Si no está autenticado, muestra el login federado */}
      {!isAuthenticated && (
        <div className="flex justify-center my-8">
          <FederatedLogin />
        </div>
      )}
      <AboutUs />
      <Features />
      <ContactSection />
    </MainLayout>
  );
};

export default HomePage;