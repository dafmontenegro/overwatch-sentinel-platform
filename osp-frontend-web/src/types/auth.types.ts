export interface User {
    id: string;
    name: string;
    email: string;
    role: 'admin' | 'user';
    cameras: string[]; // IDs of cameras this user has access to
  }
  
  export interface LoginCredentials {
    email: string;
    password: string;
  }
  
  export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
  }  