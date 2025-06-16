import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import LoginPage from '../pages/LoginPage';
import LiveVideoPage from '../pages/LiveVideoPage';
import LoginCallbackPage from '../pages/LoginCallbackPage';
import PrivateRoute from './PrivateRoute';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/login/callback" element={<LoginCallbackPage />} />
      
      {/* Rutas privadas */}
      <Route path="/live" element={
        <PrivateRoute>
           <LiveVideoPage />
        </PrivateRoute>
      } />
      
      {/* Ruta para páginas no encontradas */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;