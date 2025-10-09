import axios from "axios";

const API_URL = "https://time-tracer-bottega-back.onrender.com";

console.log("🌐 API URL configured:", API_URL);

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to add token to all requests
api.interceptors.request.use(
  (config) => {
    console.log("📤 Sending request to:", config.url);
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log("🔑 Token added to request");
    }
    return config;
  },
  (error) => {
    console.error("❌ Error in request interceptor:", error);
    return Promise.reject(error);
  }
);

// Interceptor to handle authentication errors
api.interceptors.response.use(
  (response) => {
    console.log("✅ Response received:", response.status, response.data);
    return response;
  },
  (error) => {
    console.error("❌ Response error:", error);
    console.error("📄 Status:", error.response?.status);
    console.error("📄 Data:", error.response?.data);
    console.error("📄 URL:", error.config?.url);

    // ONLY logout if it's a 401 error on a request that is NOT /api/auth/me
    if (
      error.response?.status === 401 &&
      !error.config?.url?.includes("/api/auth/me") &&
      !error.config?.url?.includes("/api/auth/login")
    ) {
      console.log("🚪 Invalid token on protected request, clearing session");
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

// Authentication functions
export const authAPI = {
  login: (email, password) => {
    console.log("🔐 authAPI.login called with email:", email);
    return api.post("/api/auth/login", { email, password });
  },
  register: (userData) => api.post("/api/auth/register", userData),
  getCurrentUser: () => api.get("/api/auth/me"),
};

// User functions
export const usersAPI = {
  getAll: () => api.get("/api/users"),
  create: (userData) => api.post("/api/users", userData),
  update: (userId, userData) => api.put(`/api/users/${userId}`, userData),
  delete: (userId) => api.delete(`/api/users/${userId}`),
};

// Time entry functions
export const timeEntriesAPI = {
  getAll: () => api.get("/api/time-entries"),
  create: (entryData) => api.post("/api/time-entries", entryData),
  update: (entryId, entryData) =>
    api.put(`/api/time-entries/${entryId}`, entryData),
  delete: (entryId) => api.delete(`/api/time-entries/${entryId}`),
};

export default api;