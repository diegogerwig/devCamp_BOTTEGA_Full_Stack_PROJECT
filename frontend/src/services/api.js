import axios from 'axios';

// URL confirmada del backend
const API_URL = 'https://time-tracer-bottega-back.onrender.com';

console.log('🌐 API URL configurada:', API_URL);

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
    console.log('📤 Enviando petición a:', config.url);
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔑 Token añadido a la petición');
    }
    return config;
  },
  (error) => {
    console.error('❌ Error en interceptor de request:', error);
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => {
    console.log('✅ Respuesta recibida:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('❌ Error en respuesta:', error);
    console.error('📄 Status:', error.response?.status);
    console.error('📄 Data:', error.response?.data);
    console.error('📄 URL:', error.config?.url);
    
    // SOLO logout si es un error 401 en una petición que NO sea /api/auth/me
    if (error.response?.status === 401 && !error.config?.url?.includes('/api/auth/me')) {
      console.log('🚪 Token inválido en petición protegida, limpiando sesión');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Funciones de autenticación
export const authAPI = {
  login: (email, password) => {
    console.log('🔐 authAPI.login llamado con email:', email);
    return api.post('/api/auth/login', { email, password });
  },
  register: (userData) => api.post('/api/auth/register', userData),
  getCurrentUser: () => api.get('/api/auth/me')
};

// Funciones de usuarios
export const usersAPI = {
  getAll: () => api.get('/api/users'),
  create: (userData) => api.post('/api/users', userData),
  delete: (userId) => api.delete(`/api/users/${userId}`)
};

// Funciones de time entries
export const timeEntriesAPI = {
  getAll: () => api.get('/api/time-entries'),
  create: (entryData) => api.post('/api/time-entries', entryData),
  update: (entryId, entryData) => api.put(`/api/time-entries/${entryId}`, entryData),
  delete: (entryId) => api.delete(`/api/time-entries/${entryId}`)
};

// Función de status
export const statusAPI = {
  get: () => api.get('/api/status')
};

export default api;