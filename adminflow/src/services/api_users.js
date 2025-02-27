import { apiPost, apiGet } from './api';
import { setToken, removeToken, setRefreshToken, getRefreshToken, removeRefreshToken } from '../utils/token';

const userService = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await apiPost('/users/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.access_token) {
        setToken(response.access_token);
        
        if (response.refresh_token) {
          setRefreshToken(response.refresh_token);
        }
        
        return response;
      } else {
        throw new Error('No access token returned from server');
      }
    } catch (error) {
      removeToken();
      removeRefreshToken();
      throw error;
    }
  },

  logout: async () => {
    try {
      await apiPost('/users/logout');
      removeToken();
      removeRefreshToken();
      return { success: true };
    } catch (error) {
      removeToken();
      removeRefreshToken();
      throw error;
    }
  },

  logoutAll: async (keepCurrent = false) => {
    try {
      await apiPost(`/users/logout/all?keep_current=${keepCurrent}`);
      if (!keepCurrent) {
        removeToken();
        removeRefreshToken();
      }
      return { success: true };
    } catch (error) {
      throw error;
    }
  },

  refreshToken: async () => {
    const refreshToken = getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    try {
      // Use URLSearchParams to properly format the refresh token
      const params = new URLSearchParams();
      params.append('refresh_token', refreshToken);
      
      const response = await apiPost('/users/refresh-token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      if (response.access_token) {
        setToken(response.access_token);
        // Don't remove refresh token on successful refresh
        return response;
      }
      
      throw new Error('Failed to refresh token - no access token in response');
    } catch (error) {
      if (error.response?.status === 401) {
        // Only remove tokens on authentication failure
        removeToken();
        removeRefreshToken();
      }
      throw error;
    }
  },

  getCurrentUser: async () => {
    try {
      const response = await apiGet('/users/me');
      return response;
    } catch (error) {
      if (error.response?.status === 401) {
        removeToken();
      }
      throw error;
    }
  },

  getSessions: async () => {
    try {
      return await apiGet('/users/sessions');
    } catch (error) {
      throw error;
    }
  }
};

export default userService;