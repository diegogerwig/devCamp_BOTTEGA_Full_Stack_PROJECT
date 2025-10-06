import axios from 'axios';

const API_URL = 'https://time-tracer-bottega-back.onrender.com';

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para añadir el token a todas las peticiones
api.interceptors.request.use(
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

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Funciones de autenticación
export const authAPI = {
  login: (email, password) => api.post('/api/auth/login', { email, password }),
  register: (userData) => api.post('/api/auth/register', userData),
  getCurrentUser: () => api.get('/api/auth/me')
};

// Funciones de usuarios
export const usersAPI = {
  getAll: () => api.get('/api/users'),
  create: (userData) => api.post('/api/users', userData)
};

// Funciones de time entries
export const timeEntriesAPI = {
  getAll: () => api.get('/api/time-entries'),
  create: (entryData) => api.post('/api/time-entries', entryData)
};

// Función de status
export const statusAPI = {
  get: () => api.get('/api/status')
};

export default api;