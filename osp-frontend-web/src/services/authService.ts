
const API_URL = import.meta.env.VITE_BACK_API_URL;

export const signIn = async () => {
  
  const response = await fetch(`${API_URL}/auth/google/callback`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('Token inválido');
  }
  console.log(response.json());
  return response.json();
};

// Llama al endpoint protegido para obtener el user_id
export const fetchUserId = async (token: string): Promise<string> => {
  const response = await fetch(`${API_URL}/protected`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!response.ok) throw new Error('Token inválido');
  const data = await response.json();
  return data.user_id;
};

export const logoutUser = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
};