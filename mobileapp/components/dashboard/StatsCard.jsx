import React, { memo } from 'react';
import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Card } from "@/components/ui/card";
import { TrendingUp } from 'lucide-react-native';
import Animated from 'react-native-reanimated';

const StatsCard = memo(({ stat }) => (
  <Card
    className={`${stat.color} p-5 rounded-3xl shadow-lg mx-2 first:ml-0 last:mr-0`}
    style={{ 
      minWidth: 200,
      transform: [{ translateY: 0 }],
      elevation: 8,
    }}
  >
    <VStack space="md">
      <HStack className="items-center justify-between">
        <Box className="bg-white/25 p-4 rounded-2xl backdrop-blur-lg">
          <stat.icon size={24} color="white" strokeWidth={2.5} />
        </Box>
        <Box className={`${stat.trendUp ? 'bg-white/30' : 'bg-white/20'} px-3 py-2 rounded-full backdrop-blur-lg`}>
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
        <Text className="text-white text-4xl font-bold tracking-tight">
          {stat.value}
        </Text>
        <Text className="text-white/90 text-sm font-medium">
          {stat.title}
        </Text>
      </VStack>
    </VStack>
  </Card>
));

export default StatsCard;