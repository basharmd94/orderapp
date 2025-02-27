import React, { memo } from 'react';
import { Button } from "@/components/ui/button";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { Box } from "@/components/ui/box"; // Assuming this is the gluestack-ui Box
import { ButtonText } from "@/components/ui/button";

const QuickActionCard = memo(({ action }) => (
  <Box style={{ flex: 1 }}> {/* Simplified container */}
    <Button
      size="lg"
      variant="solid" // Fixed variant
      action="primary" // Fixed action
      className="bg-primary-500 p-5 rounded-3xl mx-2 first:ml-0 last:mr-0" // Uniform styling
      onPress={action.onPress}
    >
      <VStack space="sm" className="items-start w-full">
        <Box className="p-3 rounded-xl bg-primary-100"> {/* Uniform background */}
          <action.icon 
            size={26} 
            color="#FFA001" // Fixed icon color
            strokeWidth={2.5}
          />
        </Box>
        <VStack space="xs" className="mt-2">
          <ButtonText className="text-lg font-semibold text-white">
            {action.title}
          </ButtonText>
          <Text className="text-sm text-white/80">
            {action.description}
          </Text>
        </VStack>
      </VStack>
    </Button>
  </Box>
));

export default QuickActionCard;