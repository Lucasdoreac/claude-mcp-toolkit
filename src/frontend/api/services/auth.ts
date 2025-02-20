/**
 * Authentication API service.
 */
import apiClient from '../client';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<Token> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post<Token>('/auth/token', formData);
    apiClient.setToken(response.access_token);
    return response;
  }

  async register(data: RegisterData): Promise<User> {
    return apiClient.post<User>('/auth/users', data);
  }

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/users/me');
  }

  async updateUser(data: Partial<User>): Promise<User> {
    return apiClient.put<User>('/auth/users/me', data);
  }

  logout() {
    apiClient.clearToken();
  }

  isAuthenticated(): boolean {
    return !!apiClient.getToken();
  }
}

export const authService = new AuthService();
export default authService;