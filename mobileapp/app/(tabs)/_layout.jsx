import { router, Tabs } from 'expo-router';
import { Platform } from 'react-native';
import { House, Package, User, ShoppingBag, CirclePlus, Send, ChevronLeft } from 'lucide-react-native';
import { Box } from '@/components/ui/box';
import { Text } from '@/components/ui/text';
import { Pressable } from '@/components/ui/pressable';

const TabBarIcon = ({ focused, color, icon: Icon }) => {
  return (
    <Box className="items-center justify-center">
      <Icon 
        size={24} 
        color={color} 
        strokeWidth={focused ? 2.5 : 1.5}
      />
    </Box>
  );
};

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#FFA001',
        tabBarInactiveTintColor: '#A8A8A8',
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#fff',
          height: 60,
          paddingTop: 5,
          borderTopWidth: 1,
          borderTopColor: '#f3f4f6',
        },
        tabBarItemStyle: {
          paddingVertical: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        unmountOnBlur: true,
        lazy: true,
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: 'Home',
          tabBarIcon: (props) => (
            <TabBarIcon {...props} icon={House} />
          ),
        }}
      />
      <Tabs.Screen
        name="create-order"
        options={{
          title: 'CreateOrder',
          headerShown: true,
          headerTitle: 'Create Order',  
          headerStyle: {
            backgroundColor: "#DE7123", // Change to your desired color    
          },
          headerShadowVisible: false, // React Navigation 6+
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
          tabBarIcon: (props) => (
            <TabBarIcon {...props} icon={CirclePlus} />
          ),

      
        }}
      />
      <Tabs.Screen
        name="send-orders"
        options={{
          title: 'SendOrders',
          headerShown: true,
          headerTitle: 'Send Orders',
          
          headerTitleStyle: {
            fontSize: 16,
            fontWeight: '600',
          },
          headerStyle: {
            backgroundColor: "#DE7123", // Change to your desired color    
          },
          headerShadowVisible: false, // React Navigation 6+
          headerLeft: () => (
            <Box className="ml-4">
              <Pressable onPress={() => router.back()}>
                <ChevronLeft size={24} color="#fff" />
              </Pressable>
            </Box>
          ),
          tabBarIcon: (props) => (
            <TabBarIcon {...props} icon={Send} />
          ),
        }}
      />
            <Tabs.Screen
        name="latest-orders"
        options={{
          title: 'LatestOrders',
          tabBarIcon: (props) => (
            <TabBarIcon {...props} icon={User} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: (props) => (
            <TabBarIcon {...props} icon={User} />
          ),
        }}
      />

    </Tabs>
  );
}
