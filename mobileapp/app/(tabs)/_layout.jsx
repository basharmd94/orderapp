import { router, Tabs } from 'expo-router';
import { Platform } from 'react-native';
import { House, Package, User, ShoppingBag, CirclePlus, Send, ChevronLeft } from 'lucide-react-native';
import { Box } from '@/components/ui/box';
import { Text } from '@/components/ui/text';
import { Pressable } from '@/components/ui/pressable';
import { useCallback } from 'react';

const TabBarIcon = ({ focused, color, icon: Icon }) => {
  return (
    <Box className="items-center justify-center">
      <Icon 
        size={23} 
        color={color} 
        strokeWidth={focused ? 2 : 1.5}
      />
    </Box>
  );
};

export default function TabLayout() {
  // Pre-render tab headers to avoid re-renders during navigation
  const renderHomeTabIcon = useCallback((props) => <TabBarIcon {...props} icon={House} />, []);
  const renderCreateTabIcon = useCallback((props) => <TabBarIcon {...props} icon={CirclePlus} />, []);
  const renderSendTabIcon = useCallback((props) => <TabBarIcon {...props} icon={Send} />, []);
  const renderProfileTabIcon = useCallback((props) => <TabBarIcon {...props} icon={User} />, []);
  
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#FFA001',
        tabBarInactiveTintColor: '#A8A8A8',
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#fff',
          height: 60,
          paddingHorizontal: 8,
          borderTopWidth: 1,
          borderTopColor: '#f3f4f6',
        },
        tabBarItemStyle: {
          paddingVertical: 8,
        },
        tabBarLabelStyle: {
          fontSize: 10,
          fontWeight: '500',
        },
        // Optimized tab navigation performance
        unmountOnBlur: false,
        lazy: true,
        freezeOnBlur: false, // Prevents freezing UI when tab is not focused
        detachInactiveScreens: false, // Keep inactive screens attached for faster switching
        detachPreviousScreen: false,
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: 'Home',
          tabBarIcon: renderHomeTabIcon,
        }}
      />
      <Tabs.Screen
        name="create-order"
        options={{
          title: 'Create',
          headerShown: false,
          headerTitle: 'Create',  
          headerStyle: {
            backgroundColor: "#DE7123",    
          },
          headerShadowVisible: false,
          headerTitleStyle: {
            fontSize: 16,
            fontWeight: '600',
          },
          headerLeft: () => (
            <Box className="ml-4">
              <Pressable onPress={() => router.back()}>
                <ChevronLeft size={24} color="#fff" />
              </Pressable>
            </Box>
          ),
          tabBarIcon: renderCreateTabIcon,
        }}
      />
      <Tabs.Screen
        name="send-orders"
        options={{
          title: 'Send',
          headerShown: false,
          headerTitle: 'Send Orders',
          headerTitleStyle: {
            fontSize: 16,
            fontWeight: '600',
          },
          headerStyle: {
            backgroundColor: "#DE7123",
          },
          headerShadowVisible: false,
          headerLeft: () => (
            <Box className="ml-4">
              <Pressable onPress={() => router.back()}>
                <ChevronLeft size={24} color="#fff" />
              </Pressable>
            </Box>
          ),
          tabBarIcon: renderSendTabIcon,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: renderProfileTabIcon,
        }}
      />
    </Tabs>
  );
}
