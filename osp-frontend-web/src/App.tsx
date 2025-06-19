import React from 'react';
import { AuthProvider } from './context/AuthContext';
import AppRoutes from './routes/AppRoutes';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className="min-h-screen flex flex-col">
        <AppRoutes />
      </div>
    </AuthProvider>
  );
};

export default App;