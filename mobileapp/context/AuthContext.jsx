import { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { login as apiLogin, logout as apiLogout, getCurrentUser } from '@/lib/api_users';
import { router } from 'expo-router';

const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const token = await AsyncStorage.getItem('accessToken');
      if (token) {
        const userInfo = await getCurrentUser();
        console.log('Retrieved user info:', userInfo); // Debug log
        setUser(userInfo);
        router.replace('/(tabs)/home');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      await AsyncStorage.removeItem('accessToken');
      await AsyncStorage.removeItem('refreshToken');
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const { access_token, refresh_token } = await apiLogin(username, password);
      await AsyncStorage.setItem('accessToken', access_token);
      await AsyncStorage.setItem('refreshToken', refresh_token);
      
      // Immediately fetch user info after successful login
      const userInfo = await getCurrentUser();
      console.log('Login user info:', userInfo); // Debug log
      setUser(userInfo);
      router.replace('/(tabs)/home');
      return true;
    } catch (error) {
      console.error('Login failed:', error?.response?.data || error.message);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      await AsyncStorage.removeItem('accessToken');
      await AsyncStorage.removeItem('refreshToken');
      setUser(null);
      router.replace('/sign-in');
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);