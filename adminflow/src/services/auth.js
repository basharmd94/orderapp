import userService from './api_users';
import { isAuthenticated, clearToken, getUserData, setUserData } from '../utils/token';

const authService = {
  login: async (username, password) => {
    try {
      const response = await userService.login(username, password);
      
      // Store user data if needed
      if (response.user) {
        setUserData(response.user);
      } else {
        // If user data isn't included in login response, fetch it
        try {
          const userData = await userService.getCurrentUser();
          if (userData) {
            setUserData(userData);
          }
        } catch (error) {
          console.error('Error fetching user data:', error);
        }
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  },

  logout: async () => {
    try {
      await userService.logout();
      clearToken();
      return { success: true };
    } catch (error) {
      // Even if server logout fails, clear tokens locally
      clearToken();
      console.error('Logout error:', error);
      return { success: true };
    }
  },
  
  isAuthenticated: () => {
    return isAuthenticated();
  },
  
  getUserInfo: () => {
    return getUserData();
  },

  refreshSession: async () => {
    if (!isAuthenticated()) {
      return false;
    }
    
    try {
      const response = await userService.refreshToken();
      if (response.access_token) {
        // Get fresh user data after token refresh
        try {
          const userData = await userService.getCurrentUser();
          if (userData) {
            setUserData(userData);
          }
        } catch (userError) {
          console.error('Error updating user data after refresh:', userError);
        }
        return true;
      }
      return false;
    } catch (error) {
      console.error('Token refresh failed:', error);
      if (error.response?.status === 401) {
        clearToken(); // Clear tokens on authentication failure
      }
      return false;
    }
  },

  // Add auto-refresh mechanism with more frequent checks
  setupTokenRefresh: () => {
    const REFRESH_INTERVAL = 10 * 60 * 1000; // Refresh every 10 minutes
    let failedAttempts = 0;
    const MAX_RETRY_ATTEMPTS = 3;
    
    const refreshInterval = setInterval(async () => {
      if (isAuthenticated()) {
        try {
          const success = await authService.refreshSession();
          if (success) {
            failedAttempts = 0; // Reset failed attempts on success
          } else {
            failedAttempts++;
            if (failedAttempts >= MAX_RETRY_ATTEMPTS) {
              console.error('Max refresh retry attempts reached');
              clearInterval(refreshInterval);
              clearToken(); // Force logout after max retries
              window.location.href = '/pages/login'; // Redirect to login
            }
          }
        } catch (error) {
          console.error('Error in refresh interval:', error);
          failedAttempts++;
        }
      } else {
        clearInterval(refreshInterval);
      }
    }, REFRESH_INTERVAL);

    // Return cleanup function
    return () => clearInterval(refreshInterval);
  }
};

export default authService;
