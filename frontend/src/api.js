// frontend/src/api.js
import axios from "axios";

// Use Vite env or fallback to localhost:5000
const baseURL = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";

const api = axios.create({
  baseURL,
});

// Request interceptor attaches token (if present) to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("pixclad_token");
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
