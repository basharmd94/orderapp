import apiClient from '../utils/apiClient';

export const authService = {
  login: async (username, password) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const response = await apiClient.post('/users/login', params);
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post('/users/logout');
    return response.data;
  },

  refreshToken: async (refreshToken) => {
    const params = new URLSearchParams();
    params.append('refresh_token', refreshToken);
    
    const response = await apiClient.post('/users/refresh-token', params);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },

  getUserSessions: async () => {
    const response = await apiClient.get('/users/sessions');
    return response.data;
  },

  logoutAllSessions: async (keepCurrent = false) => {
    const response = await apiClient.post('/users/logout/all', null, {
      params: { keep_current: keepCurrent }
    });
    return response.data;
  }
};