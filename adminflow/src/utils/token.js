// Token utility functions for storing and retrieving authentication tokens

// Constants for storage keys
const ACCESS_TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_DATA_KEY = 'user_data';

// Get the stored token
export const getToken = () => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

// Set the token in storage
export const setToken = (token) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
};

// Remove the token from storage
export const removeToken = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
};

// Get the stored refresh token
export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

// Set the refresh token in storage
export const setRefreshToken = (token) => {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

// Remove the refresh token from storage
export const removeRefreshToken = () => {
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

// Store user data
export const setUserData = (userData) => {
  localStorage.setItem(USER_DATA_KEY, JSON.stringify(userData));
};

// Get stored user data
export const getUserData = () => {
  const userData = localStorage.getItem(USER_DATA_KEY);
  if (userData) {
    try {
      return JSON.parse(userData);
    } catch (e) {
      console.error('Error parsing user data:', e);
      return null;
    }
  }
  return null;
};

// Remove user data
export const removeUserData = () => {
  localStorage.removeItem(USER_DATA_KEY);
};

// Clear all auth data
export const clearToken = () => {
  removeToken();
  removeRefreshToken();
  removeUserData();
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!getToken();
};