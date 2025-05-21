import React from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Hero from '../components/home/Hero';
import AboutUs from '../components/home/AboutUs';
import Features from '../components/home/Features';
import ContactSection from '../components/home/ContactSection';
import useAuth from '../hooks/useAuth';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { loginWithProvider } = useAuth();

  const handleDirectAccess = async () => {
    try {
      await loginWithProvider('direct');
      navigate('/live');
    } catch (error) {
      console.error('Error al iniciar sesión:', error);
    }
  };

  return (
    <MainLayout>
      <Hero 
        title="OSP - Overwatch Sentinel Platform" 
        subtitle="Vigilancia inteligente basada en visión por computadora" 
        ctaText="Acceder al Sistema" 
        onCtaClick={handleDirectAccess} 
      />
      <AboutUs />
      <Features />
      <ContactSection />
    </MainLayout>
  );
};

export default HomePage;