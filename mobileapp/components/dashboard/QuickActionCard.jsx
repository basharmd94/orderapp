import React, { memo } from 'react';
import { Button } from "@/components/ui/button";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { Box } from "@/components/ui/box";
import { ButtonText } from "@/components/ui/button";
import Animated from 'react-native-reanimated';

const QuickActionCard = memo(({ action }) => (
  <Animated.View style={{ flex: 1 }}>
    <Button
      size="lg"
      variant={action.primary ? "solid" : "outline"}
      action={action.primary ? "primary" : "secondary"}
      className={`
        ${action.primary ? 'bg-gradient-to-br from-primary-500 to-primary-600' : 'bg-white'} 
        p-5 rounded-3xl shadow-lg mx-2 first:ml-0 last:mr-0
      `}
      style={{
        height: 160,
        shadowColor: action.primary ? '#FFA001' : '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: action.primary ? 0.3 : 0.1,
        shadowRadius: 8,
        elevation: 5,
      }}
      onPress={action.onPress}
    >
      <VStack space="sm" className="items-start w-full">
        <Box 
          className={`
            p-3 rounded-xl 
            ${action.primary ? 'bg-white/20 backdrop-blur-lg' : 'bg-primary-50'}
          `}
        >
          <action.icon 
            size={26} 
            color={action.primary ? "#fff" : "#FFA001"} 
            strokeWidth={2.5}
          />
        </Box>
        <VStack space="xs" className="mt-2">
          <ButtonText 
            className={`
              text-lg font-semibold 
              ${action.primary ? 'text-white' : 'text-gray-900'}
            `}
          >
            {action.title}
          </ButtonText>
          <Text 
            className={`
              text-sm 
              ${action.primary ? 'text-white/80' : 'text-gray-500'}
            `}
          >
            {action.description}
          </Text>
        </VStack>
      </VStack>
    </Button>
  </Animated.View>
));

export default QuickActionCard;