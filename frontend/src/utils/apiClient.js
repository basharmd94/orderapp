import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
});

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Keep form-urlencoded for POST requests with URLSearchParams
        if (config.method === 'post' && config.data instanceof URLSearchParams) {
            config.headers['Content-Type'] = 'application/x-www-form-urlencoded';
        } else if (config.method !== 'post') {
            // For other requests (GET, etc), use JSON
            config.headers['Content-Type'] = 'application/json';
        }
        
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Handle 401 errors and token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refreshToken');
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }

                const params = new URLSearchParams();
                params.append('refresh_token', refreshToken);

                const response = await apiClient.post('/users/refresh-token', params);
                const { access_token } = response.data;
                
                localStorage.setItem('accessToken', access_token);
                originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
                
                return apiClient(originalRequest);
            } catch (refreshError) {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default apiClient;