import React from 'react';
import TextLogo from '../assets/Logo-CapriBlue.svg';

interface AuthLayoutProps {
  children: React.ReactNode;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-whitegray via-gray-50 to-caprilight/20 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="flex justify-center -mb-8">
          <div className="transform transition-transform duration-300 hover:scale-105">
            <img 
              src={TextLogo} 
              alt="OSP Overwatch Sentinel Platform" 
              className="h-64 w-auto drop-shadow-lg" 
            />
          </div>
        </div>

        <div className="bg-white/95 backdrop-blur-sm py-8 px-12 shadow-2xl rounded-2xl border border-gray-200/50 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-capri/5 via-transparent to-caprilight/5 pointer-events-none"></div>

          <div className="relative z-10">
            {children}
          </div>
        </div>

        <div className="text-center mt-8">
          <p className="text-xs text-asphaltlight/70 font-medium">
            © 2025 OSP Sentinel Platform. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;