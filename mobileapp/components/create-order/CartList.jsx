import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { Card } from "@/components/ui/card";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Divider } from "@/components/ui/divider";
import { ScrollView } from "react-native";
import { Toast } from "@/components/ui/toast";
import CartItem from "./CartItem";

export default function CartList({ 
  cartItems, 
  customerName, 
  onRemoveItem 
}) {
  const toast = Toast;

  const calculateTotal = () => {
    return cartItems.reduce((sum, item) => sum + item.xlinetotal, 0);
  };

  if (cartItems.length === 0) return null;

  return (
    <Box className="w-full mb-15 "> {/* Added margin bottom for spacing */}
      <Card className="w-full overflow-hidden border-lg shadow-lg relative md:max-w-md ml-auto md:h-[300px] h-[470px]">
        <VStack space="md" className="h-full">
          {/* Cart Header */}
          <Box className="px-6 py-3 md:py-4 bg-warning-400 rounded-t-lg z-10">
            <HStack space="3" alignItems="center">
              <Text className="text-base md:text-lg font-semibold text-white truncate">
                {customerName.length > 25 ? customerName.substring(0, 25) + "..." : customerName}
              </Text>
            </HStack>
          </Box>

          {/* Scrollable Cart Items */}
          <ScrollView 
            className="flex-1 px-2 md:px-1"
            showsVerticalScrollIndicator={false}
          >
            <VStack space="0" className="bg-gray-50/50 pb-12">
              {cartItems.map((item, index) => (
                <Box key={item.xsl}>
                  {index > 0 && <Divider className="my-1 md:my-2 opacity-20" />}
                  <CartItem item={item} onRemove={onRemoveItem} />
                </Box>
              ))}
            </VStack>
          </ScrollView>

          {/* Cart Footer */}
          <Box className="px-3 py-2 md:py-3 bg-gradient-to-r from-gray-100 to-gray-300 border-t border-gray-200 rounded-b-lg">
            <HStack justifyContent="space-between" alignItems="center">
              <VStack space="1">
                <Box className="bg-primary-50/80 px-2 py-0.5 md:px-2.5 md:py-1 rounded-full">
                  <Text className="text-xs font-medium text-primary-800">
                    {cartItems.length} {cartItems.length === 1 ? 'Item' : 'Items'}
                  </Text>
                </Box>
                <Text className="text-xs font-medium text-gray-600">
                  Total Amount
                </Text>
                <Text className="text-lg md:text-xl font-extrabold text-gray-900">
                  ৳{calculateTotal()}
                </Text>
              </VStack>
            </HStack>
          </Box>
        </VStack>
      </Card>
    </Box>
  );
}