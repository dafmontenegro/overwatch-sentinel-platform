export interface User {
  id: string;
  name: string;
  email: string;
  picture?: string;
  provider: string;
  provider_id?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface UserResponse {
  user: User;
}
  
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}  