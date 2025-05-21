import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import NavItem from './NavItem';
import useAuth from '../../hooks/useAuth';
import Logo from '../../assets/Logo.svg';

const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { isAuthenticated, loginWithProvider, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  const handleDirectLogin = async () => {
    try {
      // Simulamos un inicio de sesión automático
      await loginWithProvider('direct');
      // Redirigimos al dashboard
      navigate('/');
    } catch (error) {
      console.error('Error al iniciar sesión:', error);
    }
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-6 py-3">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <img src={Logo} alt="Logo" className="h-10 w-auto" />
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8 text-capri">
            <NavItem 
              to="/" 
              label="Inicio" 
              active={location.pathname === '/'} 
              onClick={closeMenu}
            />
            
            {isAuthenticated ? (
              <>
                <NavItem to="/live" label="Video en Vivo" active={location.pathname === '/live'} onClick={closeMenu} />
                {/*<NavItem to="/recordings" label="Grabaciones" active={location.pathname === '/recordings'} onClick={closeMenu} />*/}
                <button 
                  onClick={logout}
                  className="text-asphalt hover:text-capri transition duration-300"
                >
                  Cerrar Sesión
                </button>
              </>
            ) : (
              <button 
                onClick={handleDirectLogin}
                className="bg-capri text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-300"
              >
                Iniciar Sesión
              </button>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button 
              onClick={toggleMenu} 
              className="text-asphalt hover:text-capri focus:outline-none"
            >
              {isMenuOpen ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 space-y-4 pb-3">
            <NavItem to="/" label="Inicio" active={location.pathname === '/'} onClick={closeMenu} mobile />
            
            {isAuthenticated ? (
              <>
                <NavItem to="/live" label="Video en Vivo" active={location.pathname === '/live'} onClick={closeMenu} mobile />
                {/* <NavItem to="/recordings" label="Grabaciones" active={location.pathname === '/recordings'} onClick={closeMenu} mobile /> */}
                <button 
                  onClick={() => {
                    logout();
                    closeMenu();
                  }}
                  className="block w-full text-left px-4 py-2 text-asphalt hover:bg-gray-100 hover:text-capri transition duration-300"
                >
                  Cerrar Sesión
                </button>
              </>
            ) : (
              <button 
                onClick={() => {
                  handleDirectLogin();
                  closeMenu();
                }}
                className="block w-full text-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-300"
              >
                Iniciar Sesión
              </button>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;