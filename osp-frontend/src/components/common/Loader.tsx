import React from 'react';

interface LoaderProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'white' | 'gray';
  className?: string;
}

export const Loader: React.FC<LoaderProps> = ({ 
  size = 'medium', 
  color = 'primary',
  className = ''
}) => {
  // Determinar tamaño del loader
  const sizeClasses = {
    small: 'h-4 w-4 border-2',
    medium: 'h-8 w-8 border-2',
    large: 'h-12 w-12 border-3'
  };
  
  // Determinar color del loader
  const colorClasses = {
    primary: 'border-capri border-t-transparent',
    white: 'border-white border-t-transparent',
    gray: 'border-whitegray border-t-transparent'
  };
  
  return (
    <div className={`${className} flex justify-center items-center`}>
      <div 
        className={`
          ${sizeClasses[size]} 
          ${colorClasses[color]} 
          rounded-full 
          animate-spin
        `}
        role="status"
        aria-label="Cargando"
      />
      <span className="sr-only">Cargando...</span>
    </div>
  );
};

export default Loader;