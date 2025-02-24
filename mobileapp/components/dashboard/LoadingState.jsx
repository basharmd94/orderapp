import React, { useEffect } from 'react';
import { ScrollView } from 'react-native';
import { useSharedValue, withRepeat, withTiming, useAnimatedStyle } from 'react-native-reanimated';
import { Skeleton } from "@/components/ui/skeleton";
import { Box } from "@/components/ui/box";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import Animated from 'react-native-reanimated';

const LoadingState = () => {
  const pulseAnim = useSharedValue(0.3);

  useEffect(() => {
    pulseAnim.value = withRepeat(
      withTiming(0.6, { duration: 1000 }),
      -1,
      true
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: pulseAnim.value
  }));

  return (
    <Box className="px-4 py-4">
      {/* Header Skeleton */}
      <Box className="bg-gradient-to-br from-primary-500/20 to-primary-600/20 rounded-3xl p-6 shadow-sm mb-6 relative overflow-hidden">
        <HStack className="justify-between items-start">
          <VStack space="xs">
            <Animated.View style={animatedStyle}>
              <Skeleton h={4} w={100} rounded="full" startColor="primary.100" endColor="primary.200" />
            </Animated.View>
            <Animated.View style={animatedStyle}>
              <Skeleton h={8} w={200} rounded="full" startColor="primary.100" endColor="primary.200" />
            </Animated.View>
            <HStack space="sm" className="mt-1">
              <Animated.View style={animatedStyle}>
                <Skeleton h={6} w={80} rounded="full" startColor="primary.100" endColor="primary.200" />
              </Animated.View>
            </HStack>
          </VStack>
          <HStack space="sm">
            <Animated.View style={animatedStyle}>
              <Skeleton rounded="full" size="lg" startColor="primary.100" endColor="primary.200" />
            </Animated.View>
          </HStack>
        </HStack>
      </Box>
      
      {/* Stats Skeletons */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        className="mb-8"
      >
        {[1, 2, 3].map((_, index) => (
          <Box 
            key={index}
            className="bg-gradient-to-br from-gray-100 to-gray-200 p-5 rounded-3xl mr-4 relative overflow-hidden"
            style={{ minWidth: 200 }}
          >
            <VStack space="md">
              <HStack className="justify-between">
                <Animated.View style={animatedStyle}>
                  <Skeleton h={12} w={12} rounded="xl" />
                </Animated.View>
                <Animated.View style={animatedStyle}>
                  <Skeleton h={8} w={20} rounded="full" />
                </Animated.View>
              </HStack>
              <VStack space="xs">
                <Animated.View style={animatedStyle}>
                  <Skeleton h={8} w={24} rounded="md" />
                </Animated.View>
                <Animated.View style={animatedStyle}>
                  <Skeleton h={4} w={16} rounded="full" />
                </Animated.View>
              </VStack>
            </VStack>
          </Box>
        ))}
      </ScrollView>
    </Box>
  );
};

export default LoadingState;