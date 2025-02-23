import React from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { createMaterialTopTabNavigator } from "@react-navigation/material-top-tabs";
import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";

const Tab = createMaterialTopTabNavigator();

const TodaysOrder = () => (
  <Box className="bg-white p-6 flex-1">
    <Text>Last 10 Orders</Text>
  </Box>
);

const LastDaysOrders = () => (
  <Box className="bg-white p-6 flex-1">
    <Text>Last Day's Orders</Text>
  </Box>
);

const LatestOrders = () => {
  return (
    <SafeAreaView className="bg-gray-100 flex-1 ">
      <Tab.Navigator
        screenOptions={{
          tabBarLabelStyle: { fontSize: 14, fontWeight: "bold" },
          tabBarStyle: { backgroundColor: "#ffffff" },
          tabBarActiveTintColor: "orange",
          tabBarInactiveTintColor: "gray",
          tabBarIndicatorStyle: { backgroundColor: "orange", height: 4 },
          tabBarContentContainerStyle: { paddingVertical: 15 },

           
        }}
      >
        <Tab.Screen name="Last 10 Orders" component={TodaysOrder} />
        <Tab.Screen name="Last Day's Orders" component={LastDaysOrders} />
      </Tab.Navigator>
    </SafeAreaView>
  );
};

export default LatestOrders;
