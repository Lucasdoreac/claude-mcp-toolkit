/**
 * API client configuration and base methods.
 */
import axios, { AxiosInstance } from 'axios';

// API configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 10000; // 10 seconds

// Error types
export interface ApiError {
  message: string;
  code: string;
  status: number;
}

export class ApiClient {
  private client: AxiosInstance;
  private token: string | null;

  constructor() {
    this.token = null;
    this.client = axios.create({
      baseURL: API_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const apiError: ApiError = {
          message: error.response?.data?.detail || 'An error occurred',
          code: error.response?.data?.code || 'UNKNOWN_ERROR',
          status: error.response?.status || 500,
        };

        // Handle 401 errors (unauthorized)
        if (apiError.status === 401) {
          // Clear token and redirect to login
          this.clearToken();
          window.location.href = '/login';
        }

        return Promise.reject(apiError);
      }
    );

    // Add request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  // Token management
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    return this.token || localStorage.getItem('auth_token');
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Base API methods
  async get<T>(url: string, params = {}) {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data = {}) {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  async put<T>(url: string, data = {}) {
    const response = await this.client.put<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string) {
    const response = await this.client.delete<T>(url);
    return response.data;
  }
}

// Create singleton instance
export const apiClient = new ApiClient();

export default apiClient;