import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import "../global.css";
import { GluestackUIProvider } from "@/components/ui/gluestack-ui-provider";
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import 'react-native-reanimated';

import { useColorScheme } from '@/hooks/useColorScheme';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { config } from '@gluestack-ui/config';
import { router } from 'expo-router';

// Prevent splash screen from auto-hiding before initialization
SplashScreen.preventAutoHideAsync();

function ProtectedRoute() {
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && !user) {
      router.replace('/sign-in');
    }
  }, [user, loading]);

  return null;
}

export default function RootLayout() {
  const colorScheme = useColorScheme();

  useEffect(() => {
    // Hide splash screen once everything is set
    SplashScreen.hideAsync();
  }, []);

  return (
    <GluestackUIProvider config={config}>
      <AuthProvider>
        <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
          <Stack>
            <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
            <Stack.Screen name="index" options={{ headerShown: false }} />
            <Stack.Screen name="+not-found" />
          </Stack>
          <ProtectedRoute />
          <StatusBar style={colorScheme === 'dark' ? 'light' : 'dark'} />
        </ThemeProvider>
      </AuthProvider>
    </GluestackUIProvider>
  );
}
