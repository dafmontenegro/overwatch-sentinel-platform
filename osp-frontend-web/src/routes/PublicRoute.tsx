import React from 'react';
import { useAuth } from '../hooks/useAuth';

interface PublicRouteProps {
  children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-whitegray to-lightgray">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-capri mx-auto mb-4"></div>
          <p className="text-asphaltlight">Verificando autenticación...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default PublicRoute;