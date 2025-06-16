import React from 'react';

interface AuthLayoutProps {
  children: React.ReactNode;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo de OSP */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-600 rounded-lg flex items-center justify-center">
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
          <h1 className="mt-4 text-2xl font-bold text-gray-900">
            OSP Sentinel
          </h1>
          <p className="text-sm text-gray-600">
            Overwatch Sentinel Platform
          </p>
        </div>

        {children}

        {/* Footer */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            © 2025 OSP Sentinel Platform. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;