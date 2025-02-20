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
import { AddIcon, CheckCircleIcon } from "@/components/ui/icon";
import { Spinner } from "@/components/ui/spinner";
import { useAuth } from "@/context/AuthContext";
import { useState, useEffect } from "react";
import { Send, Trash2, RefreshCcw } from "lucide-react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { createBulkOrder } from "@/lib/api_orders";
import { Heading } from "@/components/ui/heading";
import { useToast, Toast, ToastTitle, ToastDescription } from "@/components/ui/toast";

export default function SendOrders() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loadingState, setLoadingState] = useState({
    sending: false,
    refreshing: false,
    currentOrderId: null
  });
  const [showAlertDialog, setShowAlertDialog] = useState(false);
  const toast = useToast();

  const loadOrders = async () => {
    try {
      const storedOrders = await AsyncStorage.getItem("orders");
      if (storedOrders) {
        const { orders } = JSON.parse(storedOrders);
        setOrders(orders);
      }
    } catch (error) {
      console.error("Error loading orders:", error);
      showToast('error', 'Failed to load orders');
    }
  };

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
            <ToastTitle>{type === 'success' ? 'Success' : 'Error'}</ToastTitle>
            <ToastDescription>{message}</ToastDescription>
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
      
      setOrders(remainingOrders);
      await AsyncStorage.setItem("orders", JSON.stringify({ orders: remainingOrders }));
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
      
      setOrders(remainingOrders);
      await AsyncStorage.setItem("orders", JSON.stringify({ orders: remainingOrders }));
      showToast('success', 'Order deleted successfully');
    } catch (error) {
      showToast('error', 'Failed to delete order');
    }
  };

  const handleRefresh = async () => {
    setLoadingState(prev => ({ ...prev, refreshing: true }));
    await loadOrders();
    setLoadingState(prev => ({ ...prev, refreshing: false }));
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
      setOrders([]);
      await AsyncStorage.setItem("orders", JSON.stringify({ orders: [] }));
    } catch (error) {
      showToast('error', error.message || 'Failed to send orders');
    } finally {
      setLoadingState(prev => ({ ...prev, sending: false }));
      handleClose();
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView>
        <Box className="p-4">
          <HStack justifyContent="space-between" alignItems="center" className="mb-6">
            <Button
              variant="outline"
              onPress={handleRefresh}
              disabled={loadingState.refreshing || loadingState.sending}
            >
              <ButtonIcon as={RefreshCcw} className={loadingState.refreshing ? "animate-spin" : ""} />
            </Button>
          </HStack>

          {orders.length === 0 ? (
            <Card className="p-4">
              <Text className="text-center text-gray-500">No orders to send</Text>
            </Card>
          ) : (
            <VStack space="lg">
              {orders.map((order, index) => (
                <Card key={`${order.zid}-${order.xcus}-${order.items[0].xsl}`} className="w-full">
                  <VStack space="md">
                    {/* Order Header */}
                    <Box className="p-4 bg-primary-50 rounded-t-lg">
                      <HStack justifyContent="space-between" alignItems="center">
                        <VStack>
                          <Text className="font-medium">ZID: {order.zid}</Text>
                          <Text className="font-medium">{order.xcusname}</Text>
                          <Text className="text-gray-600 text-sm">{order.xcusadd}</Text>
                        </VStack>
                        <HStack space="sm">
                          <Button
                            variant="outline"
                            action="error"
                            onPress={() => deleteOrder(order)}
                          >
                            <ButtonIcon as={Trash2} />
                          </Button>
                          <Button
                            onPress={() => sendOrder(order)}
                            disabled={loadingState.sending}
                          >
                            {loadingState.sending && loadingState.currentOrderId === order.zid ? (
                              <Spinner size="small" color="$white" />
                            ) : (
                              <>
                                <ButtonIcon as={Send} />
                                <ButtonText>Send</ButtonText>
                              </>
                            )}
                          </Button>
                        </HStack>
                      </HStack>
                    </Box>

                    {/* Order Items */}
                    <VStack space="sm" className="p-4">
                      {order.items.map((item, itemIndex) => (
                        <Box key={item.xsl}>
                          {itemIndex > 0 && <Divider className="my-2" />}
                          <HStack justifyContent="space-between" alignItems="center">
                            <VStack space="xs" flex={1}>
                              <Text className="font-medium">{item.xdesc}</Text>
                              <Text className="text-gray-600">
                                {item.xqty} × ৳{item.xprice} = ৳{item.xlinetotal}
                              </Text>
                            </VStack>
                          </HStack>
                        </Box>
                      ))}
                    </VStack>

                    {/* Order Footer */}
                    <Box className="p-4 bg-gray-50 rounded-b-lg">
                      <HStack justifyContent="space-between" alignItems="center">
                        <Text className="font-medium">Total Amount:</Text>
                        <Text className="font-bold text-lg">৳{calculateTotal(order.items)}</Text>
                      </HStack>
                    </Box>
                  </VStack>
                </Card>
              ))}
            </VStack>
          )}
        </Box>
      </ScrollView>

      <AlertDialog
        isOpen={showAlertDialog}
        onClose={handleClose}
        size="md"
      >
        <AlertDialogBackdrop />
        <AlertDialogContent>
          <AlertDialogHeader>
            <Heading size="md">Confirm Send All Orders</Heading>
          </AlertDialogHeader>
          <AlertDialogBody>
            <Text>Are you sure you want to send {orders.length} orders?</Text>
          </AlertDialogBody>
          <AlertDialogFooter>
            <Button
              variant="outline"
              action="secondary"
              onPress={handleClose}
              size="sm"
              marginRight="$2"
            >
              <ButtonText>Cancel</ButtonText>
            </Button>
            <Button
              size="sm"
              action="positive"
              onPress={handleBulkSend}
              isDisabled={loadingState.sending}
            >
              <ButtonText>{loadingState.sending ? 'Sending...' : 'Send All'}</ButtonText>
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <Fab
        size="lg"
        placement="bottom right"
        isDisabled={loadingState.sending || orders.length === 0}
        onPress={() => setShowAlertDialog(true)}
        m="$4"
      >
        {loadingState.sending ? (
          <Spinner size="small" color="$white" />
        ) : (
          <>
            <FabIcon as={AddIcon} />
            <FabLabel>Send All</FabLabel>
          </>
        )}
      </Fab>
    </SafeAreaView>
  );
}