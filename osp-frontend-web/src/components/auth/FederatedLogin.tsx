import React from 'react';
import { useAuth } from '../../hooks/useAuth';

const API_URL = import.meta.env.VITE_BACK_API_URL;

const FederatedLogin: React.FC = () => {
  const handleGoogleLogin = () => {
    window.location.href = `${API_URL}/auth/google`;
  };

  return (
    <button
      className="w-full py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700 flex items-center justify-center gap-2"
      onClick={handleGoogleLogin}
    >
      <svg className="w-5 h-5" viewBox="0 0 24 24">
        <path fill="currentColor" d="M12.545 10.239v3.821h5.445c-.712 2.315-2.647 3.972-5.445 3.972a6.033 6.033 0 110-12.064c1.498 0 2.866.549 3.921 1.453l2.814-2.814A9.969 9.969 0 0012.545 2C7.021 2 2.545 6.477 2.545 12s4.476 10 10 10c5.523 0 10-4.477 10-10a9.982 9.982 0 00-2-5.945l-3.46 3.461z"/>
      </svg>
      Continuar con Google
    </button>
  );
};

export default FederatedLogin;