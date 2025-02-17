import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Check if user is logged in on component mount
        const token = localStorage.getItem('accessToken');
        if (token) {
            checkAuthStatus();
        } else {
            setLoading(false);
        }
    }, []);

    const processUserData = (userData) => {
        // Ensure businessId is properly formatted
        if (userData.businessId) {
            userData.businessId = Array.isArray(userData.businessId) 
                ? parseInt(userData.businessId[0]) 
                : parseInt(userData.businessId);
        }

        // Ensure is_admin is a string
        if (typeof userData.is_admin === 'boolean') {
            userData.is_admin = userData.is_admin ? 'admin' : 'user';
        }

        return userData;
    };

    const checkAuthStatus = async () => {
        try {
            const response = await axios.get('/api/v1/users/me', {
                headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` }
            });
            setUser(processUserData(response.data));
        } catch (error) {
            if (error.response?.status === 401) {
                // Try to refresh token
                await refreshToken();
            }
        } finally {
            setLoading(false);
        }
    };

    const refreshToken = async () => {
        try {
            const refreshToken = localStorage.getItem('refreshToken');
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }

            const response = await axios.post('/api/v1/users/refresh-token', {
                refresh_token: refreshToken
            });

            localStorage.setItem('accessToken', response.data.access_token);
            await checkAuthStatus();
        } catch (error) {
            logout();
            setError('Session expired. Please login again.');
        }
    };

    const login = async (username, password) => {
        try {
            setError(null);
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post('/api/v1/users/login', formData);
            
            localStorage.setItem('accessToken', response.data.access_token);
            localStorage.setItem('refreshToken', response.data.refresh_token);
            
            await checkAuthStatus();
            return { success: true };
        } catch (error) {
            setError(error.response?.data?.detail || 'An error occurred during login');
            return { success: false, error: error.response?.data?.detail };
        }
    };

    const logout = async () => {
        try {
            const token = localStorage.getItem('accessToken');
            if (token) {
                await axios.post('/api/v1/users/logout', {}, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            setUser(null);
        }
    };

    const value = {
        user,
        loading,
        error,
        login,
        logout,
        refreshToken
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};