import { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { login as apiLogin, logout as apiLogout, getCurrentUser } from '@/lib/api_users';
import { useSegments, useRouter } from 'expo-router';

const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    const initAuth = async () => {
      const userInfo = await checkUser();
      if (userInfo) {
        setUser(userInfo);
        if (segments[0] !== '(tabs)') {
          router.replace('/(tabs)/home');
        }
      } else {
        if (segments[0] !== 'sign-in') {
          router.replace('/sign-in');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [segments]);

  const checkUser = async () => {
    try {
      const [token, refreshToken] = await Promise.all([
        AsyncStorage.getItem('accessToken'),
        AsyncStorage.getItem('refreshToken')
      ]);

      if (!token || !refreshToken) {
        throw new Error('No tokens available');
      }

      const userInfo = await getCurrentUser();
      return userInfo;
    } catch (error) {
      console.error('Auth check failed:', error);
      await Promise.all([
        AsyncStorage.removeItem('accessToken'),
        AsyncStorage.removeItem('refreshToken')
      ]);
      return null;
    }
  };

  const login = async (username, password) => {
    try {
      const { access_token, refresh_token } = await apiLogin(username, password);
      await Promise.all([
        AsyncStorage.setItem('accessToken', access_token),
        AsyncStorage.setItem('refreshToken', refresh_token)
      ]);

      const userInfo = await getCurrentUser();
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
      await Promise.all([
        AsyncStorage.removeItem('accessToken'),
        AsyncStorage.removeItem('refreshToken')
      ]);
      setUser(null);
      router.replace('/sign-in');
    }
  };

  const handleAuthError = async () => {
    await Promise.all([
      AsyncStorage.removeItem('accessToken'),
      AsyncStorage.removeItem('refreshToken')
    ]);
    setUser(null);
    router.replace('/sign-in');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, handleAuthError }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
