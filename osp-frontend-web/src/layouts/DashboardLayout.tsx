import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const isActivePath = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="flex h-screen bg-whitegray">
      {/* Sidebar */}
      <div 
        className={`${
          isSidebarOpen ? 'w-64' : 'w-20'
        } bg-asphalt text-white transition-all duration-300 ease-in-out flex flex-col`}
      >
        {/* Logo */}
        <div className="flex items-center justify-center h-16 border-b border-gray-700">
          {isSidebarOpen ? (
            <h1 className="text-xl font-bold">OSP Dashboard</h1>
          ) : (
            <h1 className="text-xl font-bold">OSP</h1>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-2 px-2">
            <li>
              <Link
                to="/"
                className={`flex items-center p-2 rounded-md ${
                  isActivePath('/')
                    ? 'bg-capri text-white'
                    : 'text-whitegray hover:bg-capri'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                {isSidebarOpen && <span className="ml-3">Home</span>}
              </Link>
            </li>
            <li>
              <Link
                to="/live"
                className={`flex items-center p-2 rounded-md ${
                  isActivePath('/live')
                    ? 'bg-capri text-white'
                    : 'text-whitegray hover:bg-capri'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {isSidebarOpen && <span className="ml-3">Video en Vivo</span>}
              </Link>
            </li>
            <li>
              <Link
                to="/recordings"
                className={`flex items-center p-2 rounded-md ${
                  isActivePath('/recordings')
                    ? 'bg-capri text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                {isSidebarOpen && <span className="ml-3">Grabaciones</span>}
              </Link>
            </li>
            {/* <li>
              <Link
                to="/settings"
                className={`flex items-center p-2 rounded-md ${
                  isActivePath('/settings')
                    ? 'bg-capri text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {isSidebarOpen && <span className="ml-3">Configuración</span>}
              </Link>
            </li> */}
          </ul>
        </nav>

        {/* Bottom section */}
        <div className="p-4 border-t border-gray-700">
          <button
            onClick={toggleSidebar}
            className="w-full flex items-center justify-center p-2 text-gray-300 hover:bg-gray-700 rounded-md"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={`h-6 w-6 transform ${isSidebarOpen ? '' : 'rotate-180'}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
              />
            </svg>
            {isSidebarOpen && <span className="ml-2"></span>}
          </button>
          
          <div className="mt-4">
            {user && (
              <div className={`flex ${isSidebarOpen ? 'items-center' : 'flex-col items-center'} text-sm`}>
                <div className="w-9 h-9 aspect-square flex-shrink-0 rounded-full bg-gradient-to-tr from-capri to-blue-500 flex items-center justify-center text-white font-bold shadow-lg border border-capri overflow-hidden">
                  {user.picture ? (
                    <img
                      src={user.picture}
                      alt={user.name}
                      className="w-full h-full object-cover rounded-full"
                    />
                  ) : (
                    <span className="text-lg select-none">{user.email.charAt(0).toUpperCase()}</span>
                  )}
                </div>
                {isSidebarOpen && (
                  <div className="ml-3 overflow-hidden">
                    <p className="text-white truncate">{user.name}</p>
                    <p className="text-gray-400 text-xs truncate">{user.email}</p>
                  </div>
                )}
              </div>
            )}
            
            <button
              onClick={handleLogout}
              className="mt-4 w-full flex items-center justify-center p-2 text-gray-300 hover:bg-gray-700 rounded-md"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              {isSidebarOpen && <span className="ml-2">Cerrar sesión</span>}
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top header */}
        <header className="bg-white shadow-sm z-10">
          <div className="px-4 py-3 flex justify-between items-center">
            <div className="flex items-center">
              <h2 className="text-xl font-semibold text-asphalt">
                {location.pathname === '/' && 'Home'}
                {location.pathname === '/live' && 'Video en Vivo'}
                {/* {location.pathname === '/recordings' && 'Grabaciones'} */}
                {/* {location.pathname === '/settings' && 'Configuración'} */}
              </h2>
            </div>
            {/* Notificaciones */}
            {/* <div className="flex items-center space-x-4">
              <div className="relative">
                <button className="p-1 text-gray-400 rounded-full hover:bg-whitegray focus:outline-none">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                </button>
                <span className="absolute top-0 right-0 h-2 w-2 rounded-full bg-red-500"></span>
              </div>
            </div> */}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto bg-whitegray">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;