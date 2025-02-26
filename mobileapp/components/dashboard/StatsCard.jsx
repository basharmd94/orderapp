import React, { memo } from 'react';
import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Card } from "@/components/ui/card";
import { TrendingUp } from 'lucide-react-native';
import { Platform } from 'react-native';

const StatsCard = memo(({ stat, index }) => {
  // Define individual card colors
  const getCardColor = () => {
    if (Platform.OS === 'android') {
      switch(index) {
        case 0: return 'bg-gray-800'; // Black for Total Orders
        case 1: return 'bg-orange-500'; // Orange for Pending Orders
        case 2: return 'bg-emerald-500'; // Emerald for Total Revenue
        default: return 'bg-orange-500';
      }
    } else {
      return stat.color;
    }
  };

  return (
    <Card
      style={{ 
        minWidth: 200,
        marginRight: 16, // Add consistent right margin for spacing
        elevation: Platform.OS === 'android' ? 4 : 0,
        marginBottom: 4
      }}
      className={`p-5 rounded-3xl ${getCardColor()}`}
    >
      <VStack space="md">
        <HStack className="items-center justify-between">
          <Box className="bg-white/25 p-4 rounded-2xl">
            <stat.icon size={24} color="white" strokeWidth={2.5} />
          </Box>
          <Box className={`${stat.trendUp ? 'bg-white/30' : 'bg-white/20'} px-3 py-2 rounded-full`}>
            <HStack space="xs" className="items-center">
              <TrendingUp 
                size={14} 
                color="white" 
                style={{ 
                  transform: [{ rotate: stat.trendUp ? '0deg' : '180deg' }] 
                }} 
              />
              <Text className="text-white text-xs font-semibold">
                {stat.trend}
              </Text>
            </HStack>
          </Box>
        </HStack>
        <VStack space="xs">
          <Text className="text-white text-3xl font-bold">
            {stat.value}
          </Text>
          <Text className="text-white/90 text-sm font-medium">
            {stat.title}
          </Text>
        </VStack>
      </VStack>
    </Card>
  );
});

export default StatsCard;