import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't loop if it's the login route or auth check
      if (!error.config.url.includes('/api/auth/login')) {
        localStorage.removeItem('token');
        // Let the AuthContext handle the redirect if needed
      }
    }
    return Promise.reject(error);
  }
);

export const healthApi = {
  check: () => apiClient.get('/api/health'),
};

export const authApi = {
  login: (data: FormData) => apiClient.post('/api/auth/login', data, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }),
  register: (data: any) => apiClient.post('/api/auth/register', data),
  getMe: () => apiClient.get('/api/auth/me'),
  logout: () => apiClient.post('/api/auth/logout'),
};

export const imageApi = {
  upload: (data: FormData, onUploadProgress?: (progressEvent: any) => void) => 
    apiClient.post('/api/images/upload', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    }),
  list: () => apiClient.get('/api/images'),
  get: (id: string) => apiClient.get(`/api/images/${id}`),
  delete: (id: string) => apiClient.delete(`/api/images/${id}`),
};
