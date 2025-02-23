import React, { useEffect } from 'react';
import { useSharedValue, withRepeat, withTiming, useAnimatedStyle } from 'react-native-reanimated';
import Animated from 'react-native-reanimated';

const ShimmerEffect = () => {
  const translateX = useSharedValue(-100);

  useEffect(() => {
    translateX.value = withRepeat(
      withTiming(100, { duration: 1000 }),
      -1,
      true
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <Animated.View
      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
      style={[
        {
          width: '200%',
        },
        animatedStyle
      ]}
    />
  );
};

export default ShimmerEffect;