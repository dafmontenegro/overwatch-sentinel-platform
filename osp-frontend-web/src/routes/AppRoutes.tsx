import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import LiveVideoPage from '../pages/LiveVideoPage';
//import NotFoundPage from '../pages/NotFoundPage';
import PrivateRoute from './PrivateRoute';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/" element={<HomePage />} />
      
      {/* Rutas privadas */}
      <Route path="/live" element={
        <PrivateRoute>
           <LiveVideoPage />
        </PrivateRoute>
      } />
      
      {/* Redirección al home */}
      <Route path="/login" element={<Navigate to="/" replace />} />
      
      {/* Ruta para páginas no encontradas */}
      <Route path="*" element={"No encontrado"/*<NotFoundPage />*/} />
    </Routes>
  );
};

export default AppRoutes;