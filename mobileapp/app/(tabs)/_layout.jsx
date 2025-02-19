import { Tabs } from 'expo-router';
import React from 'react';
import { Platform } from 'react-native';
import { House, Aperture } from 'lucide-react-native';
import { Box } from '@/components/ui/box';
import { Text } from '@/components/ui/text';

// import { HapticTab } from '@/components/HapticTab';
// import { IconSymbol } from '@/components/ui/IconSymbol';
// import TabBarBackground from '@/components/ui/TabBarBackground';
// import { Colors } from '@/constants/Colors';
// import { useColorScheme } from '@/hooks/useColorScheme';



const TabIcon = ({ icon, color, name, focused  }) => {
  return (
    <Box className="items-center justify-center gap-2">

      <Text className={`${focused ? 'font-semibold' : 'font-pregular'} text-xs`} style={{ color: color }}>{name}</Text>
    </Box>
  )
}




export default function TabLayout() {


  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#FFA001',
        tabBarInactiveTintColor: '#A8A8A8',
        headerShown: false,
        // tabBarButton: HapticTab,
        // tabBarBackground: TabBarBackground,
        tabBarStyle: {
          backgroundColor: '#fff',

          // borderTopColor: '#80869A',
          height: 60,
          paddingTop:5,
          // elevation: 80,
          // borderTopLeftRadius:15,
          // borderTopRightRadius:15,
          // position: 'absolute',
          // top:0
        },
        tabBarContentContainerStyle: {
          justifyContent: 'flex-end',
          paddingBottom: 50,
        },
        swipeEnabled : true,
        animationEnabled : true,
      }}>
      <Tabs.Screen
        name="home"
        options={{
          title: 'Home',
          unmountOnBlur: true, // to avoid memory leak
          lazy: true, // to improve initial load time
          swipeEnabled: true, // to enable swiping between tabs
          animationEnabled: true, // to enable animations when switching tabs
          tabBarHideOnKeyboard: true, // to hide the tab bar when the keyboard is shown 
          tabBarIcon: ({ color, focused }) => <House color={focused ? '#A8A8A8' : color} />
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          tabBarIcon: ({ color, focused }) => <Aperture color={focused ? '#A8A8A8' : color} />
        }}
      />
    </Tabs>
  );
}
