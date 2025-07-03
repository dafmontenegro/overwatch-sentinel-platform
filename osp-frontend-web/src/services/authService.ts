import type { User, UserResponse } from '../types/auth.types';

// Llama al endpoint protegido para obtener el user_id
export const fetchUserId = async (token: string): Promise<string> => {
  const response = await fetch(`/api/protected`, {
    method: 'GET',
    headers: { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) throw new Error('Token inválido');
  const data = await response.json();
  return data;
};

export const fetchUser = async (token: string): Promise<User> => {
  try {
    const response = await fetch(`/api/user/me`, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Error del servidor: ${response.status}`);
    }

    const data: UserResponse = await response.json();
    
    return data.user;
  } catch (error) {
    console.error('Error al obtener datos del usuario:', error);
    
    throw error;
  }
};

export const logoutUser = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
};