

import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { Card } from "@/components/ui/card";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Divider } from "@/components/ui/divider";
import { ScrollView, View, StyleSheet } from "react-native";
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
    <Box className="w-full mb-15">
      <Card className="w-full overflow-hidden border-lg relative md:max-w-md ml-auto shadow-sm" style={styles.cardContainer}>
        {/* Cart Header - fixed height */}
        <Box className="px-6 py-3 md:py-4 bg-gray-800 rounded-t-lg z-10">
          <HStack space="3" alignItems="center">
            <Text className="text-base md:text-lg font-semibold text-white truncate">
              {customerName.length > 25 ? customerName.substring(0, 25) + "..." : customerName}
            </Text>
          </HStack>
        </Box>

        {/* Scrollable Cart Items - fixed height with scrolling */}
        <View style={styles.scrollContainer}>
          <ScrollView 
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={true}
            nestedScrollEnabled={true}
          >
            {cartItems.map((item, index) => (
              <View key={item.xsl || index} style={styles.itemContainer}>
                {index > 0 && <Divider className="my-1 md:my-2 opacity-20" />}
                <CartItem item={item} onRemove={onRemoveItem} />
              </View>
            ))}
          </ScrollView>
        </View>

        {/* Cart Footer - fixed height */}
        <Box className="px-3 py-2 md:py-3 bg-gray-200 border-t border-gray-200 rounded-b-lg">
          <HStack justifyContent="space-between" alignItems="center">
            <VStack space="1">
              <Box className="bg-emerald-300 px-2 py-0.5 md:px-2.5 md:py-1 rounded-full">
                <Text className="text-xs font-medium text-white-800">
                  {cartItems.length} {cartItems.length === 1 ? 'Item' : 'Items'}
                </Text>
              </Box>
              <Text className="text-xs font-medium text-gray-600">
                Total Amount
              </Text>
              <Text className="text-lg md:text-xl font-extrabold text-gray-800">
                ৳{calculateTotal()}
              </Text>
            </VStack>
          </HStack>
        </Box>
      </Card>
    </Box>
  );
}

// Use StyleSheet for better performance and explicit sizing
const styles = StyleSheet.create({
  cardContainer: {
    height: 470, // Fixed height for mobile
    maxHeight: '80vh', // Limit height on larger screens
  },
  scrollContainer: {
    flex: 1,
    backgroundColor: 'rgba(249, 249, 249, 0.5)',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 8,
    paddingVertical: 8,
  },
  itemContainer: {
    marginBottom: 4,
  }
});