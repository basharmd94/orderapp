import React, { memo } from 'react';
import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Heading } from "@/components/ui/heading";
import { TrendingUp } from 'lucide-react-native';
import Animated from 'react-native-reanimated';

const ChartCard = memo(({ title, subtitle, subtitleColor, children }) => (
  <Animated.View className="bg-white rounded-3xl p-6  mb-6">
    <VStack space="md">
      <HStack className="justify-between items-center">
        <VStack>
          <Heading size="sm" className="text-gray-800">{title}</Heading>
          <Text className="text-gray-500 text-xs">Last 30 days performance</Text>
        </VStack>
        <Box className={`${subtitleColor} px-3 py-2 rounded-full`}>
          <HStack space="xs" className="items-center">
            <TrendingUp size={12} className={`${subtitleColor.replace('bg-', 'text-').replace('50', '600')}`} />
            <Text className={`${subtitleColor.replace('bg-', 'text-').replace('50', '600')} text-xs font-medium`}>
              {subtitle}
            </Text>
          </HStack>
        </Box>
      </HStack>
      <Box className="mt-2">
        {children}
      </Box>
    </VStack>
  </Animated.View>
));

export default ChartCard;