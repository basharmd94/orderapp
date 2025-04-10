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
      try {
        const userInfo = await checkUser();
        if (userInfo) setUser(userInfo);
      } catch (error) {
        console.error('Initial auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  useEffect(() => {
    if (loading) return;
    if (!user && segments[0] !== '(auth)') {
      router.replace('/sign-in');
    }
  }, [user, loading]);

  const checkUser = async () => {
    try {
      const token = await AsyncStorage.getItem('accessToken');
      if (!token) throw new Error('No tokens available');
      const userInfo = await getCurrentUser();
      return userInfo;
    } catch (error) {
      console.error('Auth check failed:', error);
      await AsyncStorage.multiRemove(['accessToken', 'refreshToken']);
      return null;
    }
  };

  const login = async (username, password) => {
    try {
      const { access_token, refresh_token } = await apiLogin(username, password);
      await AsyncStorage.multiSet([
        ['accessToken', access_token],
        ['refreshToken', refresh_token],
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
      await AsyncStorage.multiRemove(['accessToken', 'refreshToken']);
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
