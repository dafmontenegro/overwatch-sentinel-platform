import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import LoginPage from '../pages/LoginPage';
import LiveVideoPage from '../pages/LiveVideoPage';
import PrivateRoute from './PrivateRoute';
import PublicRoute from './PublicRoute';
import LoginRoute from './LoginRoute';
import RecordingsPage from '../pages/RecordingsPage';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route 
        path="/" 
        element={
          <PublicRoute>
            <HomePage />
          </PublicRoute>
        } 
      />
      <Route 
        path="/login" 
        element={
          <LoginRoute>
            <LoginPage />
          </LoginRoute>
        } 
      />
      
      {/* Rutas privadas */}
      <Route 
        path="/live" 
        element={
          <PrivateRoute>
            <LiveVideoPage />
          </PrivateRoute>
        } 
      />
      <Route 
        path="/recordings" 
        element={
          <PrivateRoute>
            <RecordingsPage />
          </PrivateRoute>
        } 
      />
      
      {/* Ruta para páginas no encontradas */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;