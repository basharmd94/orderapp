import { SafeAreaView } from "react-native-safe-area-context";
import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { ScrollView } from "react-native";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Card } from "@/components/ui/card";
import { Button, ButtonIcon, ButtonText } from "@/components/ui/button";
import { Divider } from "@/components/ui/divider";
import { Fab, FabLabel, FabIcon } from "@/components/ui/fab";
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogFooter, AlertDialogBody, AlertDialogBackdrop } from "@/components/ui/alert-dialog";
import { Spinner } from "@/components/ui/spinner";
import { useAuth } from "@/context/AuthContext";
import { useState, useEffect } from "react";
import {
  Send,
  Trash2,
  X,
  Plus,
  Package,
  ShoppingBag,
  Receipt,
  ShoppingCart,
  ArrowRight,
  BadgeCheckIcon,
  CreditCard,
  Store,
  MapPin,
  MinusCircle,
  PlusCircle,
  Calendar,
  Clock,
  Tag,
  AlertCircle,
  Check
} from 'lucide-react-native';
import AsyncStorage from "@react-native-async-storage/async-storage";
import { createBulkOrder } from "@/lib/api_orders";
import { Heading } from "@/components/ui/heading";
import { useToast, Toast, ToastTitle, ToastDescription } from "@/components/ui/toast";
import { useOrderStore } from "@/stores/orderStore";
import Animated, { useAnimatedStyle, withRepeat, withSequence, withSpring } from 'react-native-reanimated';
import { Badge, BadgeIcon, BadgeText } from "@/components/ui/badge";

export default function SendOrders() {
  const { user } = useAuth();
  const { orders, loadOrders, updateOrder } = useOrderStore();
  const [loadingState, setLoadingState] = useState({
    sending: false,
    currentOrderId: null
  });
  const [showAlertDialog, setShowAlertDialog] = useState(false);
  const toast = useToast();
  const AnimatedSend = Animated.createAnimatedComponent(Send);

  const emptyStateIconStyle = useAnimatedStyle(() => ({
    transform: [
      {
        translateY: withRepeat(
          withSequence(
            withSpring(-10),
            withSpring(0)
          ),
          -1,
          true
        )
      }
    ]
  }));

  useEffect(() => {
    loadOrders();
  }, []);

  const showToast = (type, message) => {
    const id = Math.random();
    toast.show({
      id,
      placement: 'top',
      duration: 3000,
      render: ({ id }) => {
        const uniqueToastId = "toast-" + id;
        return (
          <Toast nativeID={uniqueToastId} action={type} variant="solid">
            <VStack space="xs">
              <HStack space="sm" alignItems="center">
                {type === 'success' ? (
                  <Check size={18} className="text-white" />
                ) : (
                  <AlertCircle size={18} className="text-white" />
                )}
                <ToastTitle>{type === 'success' ? 'Success' : 'Error'}</ToastTitle>
              </HStack>
              <ToastDescription>{message}</ToastDescription>
            </VStack>
          </Toast>
        );
      },
    });
  };

  const sendOrder = async (order) => {
    setLoadingState(prev => ({ ...prev, sending: true, currentOrderId: order.zid }));
    try {
      await createBulkOrder([order]);

      const remainingOrders = orders.filter(o =>
        o.zid !== order.zid ||
        o.xcus !== order.xcus ||
        o.items[0].xsl !== order.items[0].xsl
      );

      await AsyncStorage.setItem("orders", JSON.stringify({ orders: remainingOrders }));
      await loadOrders();
      showToast('success', 'Order sent successfully!');
    } catch (error) {
      console.error("Error sending order:", error);
      showToast('error', 'Failed to send order. Please try again.');
    } finally {
      setLoadingState(prev => ({ ...prev, sending: false, currentOrderId: null }));
    }
  };

  const deleteOrder = async (order) => {
    try {
      const remainingOrders = orders.filter(o =>
        o.zid !== order.zid ||
        o.xcus !== order.xcus ||
        o.items[0].xsl !== order.items[0].xsl
      );

      await AsyncStorage.setItem("orders", JSON.stringify({ orders: remainingOrders }));
      await loadOrders();
      showToast('success', 'Order deleted successfully');
    } catch (error) {
      showToast('error', 'Failed to delete order');
    }
  };

  const updateQuantity = async (order, itemIndex, change) => {
    const updatedOrder = { ...order };
    const item = updatedOrder.items[itemIndex];
    const newQty = Math.max(1, item.xqty + change);

    updatedOrder.items[itemIndex] = {
      ...item,
      xqty: newQty,
      xlinetotal: newQty * item.xprice
    };

    const updatedOrders = orders.map(o =>
      (o.zid === order.zid && o.xcus === order.xcus) ? updatedOrder : o
    );

    await AsyncStorage.setItem("orders", JSON.stringify({ orders: updatedOrders }));
    await loadOrders();
  };

  const calculateTotal = (items) => {
    return items.reduce((sum, item) => sum + item.xlinetotal, 0);
  };

  const handleClose = () => setShowAlertDialog(false);

  const handleBulkSend = async () => {
    setLoadingState(prev => ({ ...prev, sending: true }));
    try {
      const response = await createBulkOrder(orders);
      const invoiceNumbers = response.map(order => order.xdoc).join(', ');
      showToast('success', `Orders placed successfully! Invoice numbers: ${invoiceNumbers}`);
      await AsyncStorage.setItem("orders", JSON.stringify({ orders: [] }));
      await loadOrders();
    } catch (error) {
      showToast('error', error.message || 'Failed to send orders');
    } finally {
      setLoadingState(prev => ({ ...prev, sending: false }));
      handleClose();
    }
  };

  // Delete specific Item
  const deleteItem = async (order, itemIndex) => {
    const updatedOrder = { ...order };
    
    // Remove the item from the order
    updatedOrder.items = updatedOrder.items.filter((_, index) => index !== itemIndex);
    
    // If there are no items left, delete the entire order
    if (updatedOrder.items.length === 0) {
      await deleteOrder(order);
      return;
    }

    // Update the orders array
    const updatedOrders = orders.map(o =>
      (o.zid === order.zid && o.xcus === order.xcus) ? updatedOrder : o
    );

    try {
      await AsyncStorage.setItem("orders", JSON.stringify({ orders: updatedOrders }));
      await loadOrders();
      showToast('success', 'Item deleted successfully');
    } catch (error) {
      showToast('error', 'Failed to delete item');
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Box className="px-4 py-3 bg-white shadow-sm border-b border-warning-100 w-full">
        <HStack justifyContent="space-between" alignItems="center">
          {orders.length > 0 && (
            <Badge size="md" variant="outline" action="success" className="w-full flex-1 justify-center rounded-full">
              <BadgeIcon as={ShoppingCart} className="mr-2" />
              <BadgeText className="mr-2">{orders.length} {orders.length === 1 ? 'Order' : 'Orders'}</BadgeText>
              <BadgeIcon as={Tag} className="mr-2" />
            </Badge>
          )}
        </HStack>
      </Box>

      <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
        <Box className="p-4">
          {orders.length === 0 ? (
            <Card className="bg-white shadow-xl border border-warning-200 rounded-md overflow-hidden">
              {/* Header Background */}
              <Box className="p-6 flex flex-col items-center justify-center bg-gradient-to-b from-warning-50 to-warning-100">
                {/* Icon Section */}
                <Box className="w-24 h-24 bg-warning-50 rounded-full flex items-center justify-center shadow-lg border-4 border-warning-200">
                  <Animated.View style={emptyStateIconStyle}>
                    <Send size={36} className="text-warning-500" />
                  </Animated.View>
                </Box>

                {/* Text Section */}
                <VStack space="sm" alignItems="center" className="mt-4">
                  <Text className="text-lg font-semibold text-gray-900 text-center">No Orders Yet</Text>
                  <Text className="text-sm text-gray-600 text-center max-w-[220px] leading-relaxed">
                    Create your first order to get started.
                  </Text>
                </VStack>

                {/* Plus Button (Placed Below the Text) */}
                <Box className="mt-4 w-12 h-12 bg-warning-100 rounded-full flex items-center justify-center border-4 border-white shadow-md">
                  <Plus size={20} className="text-warning-600" />
                </Box>
              </Box>
            </Card>

          ) : (
            <VStack space="lg">
              {orders.map((order, index) => (
                <Card
                  key={`${order.zid}-${order.xcus}-${order.items[0].xsl}`}
                  className="bg-white shadow-lg hover:shadow-xl border border-warning-100 rounded-2xl overflow-hidden transform transition-all duration-200 hover:-translate-y-0.5"
                >
                  <VStack space="md">
                    {/* Order Header */}
                    <Box className="px-4 py-4 bg-gradient-to-r from-warning-100 via-warning-50 to-white border-b border-warning-100">
                      <HStack justifyContent="space-between" alignItems="center">
                        <VStack>
                          <HStack space="sm" alignItems="center">
                            <Box className="bg-warning-50 px-3 py-1.5 rounded-full border border-warning-200">
                              <HStack space="xs" alignItems="center">
                                <Store size={14} className="text-warning-700" />
                                <Text className="text-xs font-semibold text-warning-700">{order.zid}</Text>
                              </HStack>
                            </Box>
                            <Box className="bg-warning-50 px-3 py-1.5 rounded-full border border-warning-200">
                              <HStack space="xs" alignItems="center">
                                <Calendar size={14} className="text-warning-700" />
                                <Text className="text-xs font-medium text-warning-700">
                                  {new Date().toLocaleDateString()}
                                </Text>
                              </HStack>
                            </Box>
                          </HStack>
                          <HStack space="xs" alignItems="center" className="mt-2">
                            <Store size={16} className="text-gray-600" />
                            <Text className="text-base font-semibold text-gray-900">{order.xcusname}</Text>
                          </HStack>
                          <HStack space="xs" alignItems="center" className="mt-0.5">
                            <MapPin size={14} className="text-gray-500" />
                            <Text className="text-xs text-gray-500">{order.xcusadd}</Text>
                          </HStack>
                        </VStack>
                        <HStack space="sm">
                          <Button
                            size="lg"
                            variant="outline"
                            action="error"
                            onPress={() => deleteOrder(order)}
                            className="rounded-full p-3.5 border-red-200 active:bg-red-50 shadow-sm"
                          >
                            <ButtonIcon as={Trash2} className="text-red-500" />
                          </Button>
                          <Button
                            size="lg"
                            onPress={() => sendOrder(order)}
                            disabled={loadingState.sending}
                            className="rounded-full p-3.5 bg-warning-500 active:bg-warning-600 shadow-sm"
                          >
                            {loadingState.sending && loadingState.currentOrderId === order.zid ? (
                              <Spinner size="small" color="$white" />
                            ) : (
                              <ButtonIcon as={Send} className="text-white" />
                            )}
                          </Button>
                        </HStack>
                      </HStack>
                    </Box>

                    {/* Order Items */}
                    <Box className="space-y-4">
                      {order.items.map((item, itemIndex) => (
                        <Box key={item.xsl} className="px-4">
                          {itemIndex > 0 && <Divider className="my-.2 opacity-10" />}
                          <VStack space="sm" className="bg-warning-50 rounded-xl py-3 px-3">
                            <HStack justifyContent="space-between" alignItems="center">
                              {/* Item Name on the left */}
                              <HStack space="sm" alignItems="center" flex={1}>
                                <Package size={18} className="text-warning-600" />
                                <Text className="text-xs font-md font-bold text-gray-500 truncate whitespace-nowrap">
                                  {item.xitem}--{item.xdesc}
                                </Text>

                              </HStack>

                              <Button
                                size="xs"
                                variant="outline"
                                onPress={() => deleteItem(order, itemIndex)}
                                className="border-none ml-auto"
                              >
                                <ButtonIcon as={Trash2} size={15} className="text-error-700" />
                              </Button>

                            </HStack>

                            <HStack justifyContent="space-between" alignItems="center" className="bg-error-50 opacity-80 p-2 rounded-xl">
                              <HStack space="sm" alignItems="center">
                                <Button
                                  size="xs"
                                  variant="outline"
                                  onPress={() => updateQuantity(order, itemIndex, -1)}
                                  className=" border-none"
                                >
                                  <ButtonIcon as={MinusCircle} size={15} className="text-warning-700" />
                                </Button>
                                <Text className="text-base font-semibold text-warning-900">{item.xqty}</Text>
                                <Button
                                  size="xs"
                                  variant="outline"
                                  onPress={() => updateQuantity(order, itemIndex, 1)}
                                  className=" border-none"
                                >
                                  <ButtonIcon as={PlusCircle} size={15} className="text-warning-700" />
                                </Button>
                              </HStack>

                              <HStack space="sm" alignItems="center">
                                <Box className="bg-white px-3 py-1.5 rounded-full border border-warning-200">
                                  <HStack space="xs" alignItems="center">
                                    <Tag size={14} className="text-warning-600" />
                                    <Text className="text-xs font-medium text-warning-700">৳{item.xprice}</Text>
                                  </HStack>
                                </Box>
                                <ArrowRight size={14} className="text-warning-400" />
                                <Box className="bg-white px-3 py-1.5 rounded-full border border-warning-200">
                                  <HStack space="xs" alignItems="center">

                                    <CreditCard size={14} className="text-warning-600" />
                                    <Text className="text-xs font-medium text-warning-700">৳{item.xlinetotal}</Text>
                                  </HStack>
                                </Box>

                              </HStack>
                            </HStack>
                          </VStack>
                        </Box>
                      ))}
                    </Box>
                    <Box className="p-4 bg-gradient-to-b from-warning-50 to-warning-100 rounded-b-lg border-t border-warning-100 w-full">
  <HStack className="w-full" justifyContent="between" alignItems="center">
    
    {/* Total Amount Label */}
    <HStack className="flex-1 items-center" space="xs">
      <Receipt size={16} className="text-warning-700" />
      <Text className="text-sm font-medium text-warning-700 leading-tight">Total Amount</Text>
    </HStack>

    {/* Value Badge - Properly Aligned */}
    <Box className="bg-white px-4 py-1 rounded-full border border-warning-200 shadow-sm">
      <HStack className="items-center space-x-1">
        <CreditCard size={14} className="text-warning-600" /> 
        <Text className="text-base font-semibold text-warning-700 leading-none">৳{calculateTotal(order.items)}</Text>
      </HStack>
    </Box>

  </HStack>
</Box>


                  </VStack>
                </Card>
              ))}
            </VStack>
          )}
        </Box>
      </ScrollView>

      {/* Alert Dialog */}
      <AlertDialog
        isOpen={showAlertDialog}
        onClose={handleClose}
        size="md"
      >
        <AlertDialogBackdrop />
        <AlertDialogContent className="bg-white flex justify-center items-center rounded-3xl mx-4">
          <AlertDialogHeader>
            <VStack space="xs" className="flex items-center">
              <Box className="w-12 h-12 bg-warning-50 rounded-full flex items-center justify-center mb-2 border-2 border-warning-100">
                <Send size={24} className="text-warning-600" />
              </Box>
              <Heading size="md" className="text-gray-900 flex justify-center items-center">Send All Orders</Heading>
              <Text className="text-sm text-gray-500 text-center">
                You are about to send {orders.length} {orders.length === 1 ? 'order' : 'orders'}
              </Text>
            </VStack>
          </AlertDialogHeader>
          <AlertDialogBody>
            <Text className="text-base text-gray-600 text-center">
              This action will submit all pending orders and cannot be undone.
            </Text>
          </AlertDialogBody>
          <AlertDialogFooter className="flex-row justify-center space-x-3 mt-4">
            <Button
              variant="outline"
              action="secondary"
              onPress={handleClose}
              size="lg"
              className="rounded-full p-3.5 border-warning-200 shadow-sm flex-1 max-w-[120px]"
            >
              <ButtonIcon as={X} className="text-gray-700" />

            </Button>
            <Button
              size="lg"
              action="positive"
              onPress={handleBulkSend}
              isDisabled={loadingState.sending}
              className="rounded-full p-3.5 bg-success-500 shadow-sm flex-1 max-w-[120px]"
            >
              {loadingState.sending ? (
                <Spinner size="small" color="$white" />
              ) : (
                <>
                  <ButtonIcon as={Send} className="text-white" />

                </>
              )}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Floating Action Button with Badge */}
      <Box className="fixed bottom-5 right-0 m-4 relative">
        {orders.length > 0 && (
          <Box
            className="absolute -top-[75px] -right-[-10px] bg-error-500 rounded-full min-w-[22px] h-[22px] flex items-center justify-center px-1.5 shadow-lg border-2 border-white z-50 transition-transform duration-200"
          >
            <Text className="text-[11px] font-bold text-white">{orders.length}</Text>
          </Box>
        )}
        <Fab
          size="lg"
          placement="bottom right"
          isDisabled={loadingState.sending || orders.length === 0}
          onPress={() => setShowAlertDialog(true)}
          className="bg-emerald-500 rounded-full shadow-xl active:scale-95 hover:scale-105 active:bg-emerald-600 p-4 transition-all duration-200"
        >
          {loadingState.sending ? (
            <Spinner size="small" color="$white" />
          ) : (
            <>
              <FabIcon as={Send} className="text-white" />

            </>
          )}
        </Fab>
      </Box>
    </SafeAreaView>
  );
}