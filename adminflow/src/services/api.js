import axios from 'axios';
import { API_BASE_URL } from '../config';
import { getToken, removeToken, removeRefreshToken } from '../utils/token';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Ensure proper content type for different request types
    if (config.data instanceof FormData) {
      config.headers['Content-Type'] = 'multipart/form-data';
    } else if (config.data instanceof URLSearchParams) {
      config.headers['Content-Type'] = 'application/x-www-form-urlencoded';
    } else {
      config.headers['Content-Type'] = 'application/json';
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Access the response data directly
    return response.data;
  },
  async (error) => {
    // Don't retry if we're already trying to refresh
    if (error.config?.url?.includes('/refresh-token')) {
      removeToken();
      removeRefreshToken();
      window.location.href = '/pages/login';
      return Promise.reject(error);
    }

    // Handle session invalid errors
    if (error.response?.status === 401 && error.response?.data?.detail === "Invalid session") {
      removeToken();
      removeRefreshToken();
      window.location.href = '/pages/login';
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && error.response?.data?.detail === "Could not validate credentials") {
      removeToken();
      removeRefreshToken();
      window.location.href = '/pages/login';
    }

    return Promise.reject(error?.response?.data || error);
  }
);

export const apiGet = async (url, config = {}) => {
  try {
    return await api.get(url, config);
  } catch (error) {
    throw error;
  }
};

export const apiPost = async (url, data = {}, config = {}) => {
  try {
    return await api.post(url, data, config);
  } catch (error) {
    throw error;
  }
};

export const apiPut = async (url, data = {}, config = {}) => {
  try {
    return await api.put(url, data, config);
  } catch (error) {
    throw error;
  }
};

export const apiDelete = async (url, config = {}) => {
  try {
    return await api.delete(url, config);
  } catch (error) {
    throw error;
  }
};

export default api;