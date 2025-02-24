import { Platform } from 'react-native';

// Use localhost for iOS and 10.0.2.2 for Android emulator
export const BACKEND_URL = Platform.select({
    ios: 'http://127.0.0.1:8000/api/v1',
    android: 'http://10.0.2.2:8000/api/v1',
    default: 'http://127.0.0.1:8000/api/v1'
});

export const API_TIMEOUT = 15000; // 15 seconds