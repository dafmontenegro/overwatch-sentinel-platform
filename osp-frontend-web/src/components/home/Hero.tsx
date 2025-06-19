import React from 'react';

interface HeroProps {
  title: string;
  subtitle: string;
  ctaText: string;
  onCtaClick: () => void;
}

const Hero: React.FC<HeroProps> = ({ title, subtitle, ctaText, onCtaClick }) => {
  return (
    <div className="bg-gradient-to-r from-asphalt to-capri text-white">
      <div className="container mx-auto px-6 py-16 md:py-24 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold mb-4">
          {title}
        </h1>
        <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
          {subtitle}
        </p>
        <button 
          onClick={onCtaClick} 
          className="bg-white text-capri font-medium py-3 px-8 rounded-lg shadow-md hover:bg-blue-50 transition duration-300"
        >
          {ctaText}
        </button>
      </div>
    </div>
  );
};

export default Hero;