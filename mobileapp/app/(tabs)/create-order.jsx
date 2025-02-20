import { SafeAreaView } from "react-native-safe-area-context";
import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { Heading } from "@/components/ui/heading";
import { ScrollView } from "react-native";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Input, InputField, InputIcon, InputSlot } from "@/components/ui/input";
import { Button, ButtonIcon, ButtonText } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Divider } from "@/components/ui/divider";
import { Spinner } from "@/components/ui/spinner";
import {
  Drawer,
  DrawerBackdrop,
  DrawerContent,
  DrawerHeader,
  DrawerBody,
  DrawerFooter
} from "@/components/ui/drawer";


import { useAuth } from "@/context/AuthContext";
import { useState, useEffect, useCallback } from "react";
import { ChevronDown, Search, ShoppingCart, Trash2, X } from "lucide-react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import api from "@/lib/api";

export default function CreateOrder() {
  const { user } = useAuth();
  const [zid, setZid] = useState("");
  const [customer, setCustomer] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerAddress, setCustomerAddress] = useState("");
  const [item, setItem] = useState("");
  const [itemName, setItemName] = useState("");
  const [itemPrice, setItemPrice] = useState(0);
  const [quantity, setQuantity] = useState("");

  const [showZidSheet, setShowZidSheet] = useState(false);
  const [showCustomerSheet, setShowCustomerSheet] = useState(false);
  const [showItemSheet, setShowItemSheet] = useState(false);
  const [customerSearchText, setCustomerSearchText] = useState("");
  const [itemSearchText, setItemSearchText] = useState("");

  const [customers, setCustomers] = useState([]);
  const [items, setItems] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [customerOffset, setCustomerOffset] = useState(0);
  const [itemOffset, setItemOffset] = useState(0);
  const [loadingMoreCustomers, setLoadingMoreCustomers] = useState(false);
  const [loadingMoreItems, setLoadingMoreItems] = useState(false);
  const [hasMoreCustomers, setHasMoreCustomers] = useState(true);
  const [hasMoreItems, setHasMoreItems] = useState(true);

  const zids = [100000, 100001, 100005];
  const LIMIT = 10;

  // Load cart items from storage on mount
  useEffect(() => {
    loadCartItems();
  }, []);

  // Reset pagination when search text changes
  useEffect(() => {
    setCustomerOffset(0);
    setHasMoreCustomers(true);
  }, [customerSearchText]);

  useEffect(() => {
    setItemOffset(0);
    setHasMoreItems(true);
  }, [itemSearchText]);

  const loadCartItems = async () => {
    try {
      const storedCart = await AsyncStorage.getItem("cartItem");
      if (storedCart) {
        const cart = JSON.parse(storedCart);
        setCartItems(cart.items || []);
        if (cart.zid) {
          setZid(cart.zid);
          setCustomer(cart.xcus);
          setCustomerName(cart.xcusname);
          setCustomerAddress(cart.xcusadd);
        }
      }
    } catch (error) {
      console.error("Error loading cart items:", error);
    }
  };

  const searchCustomers = async (searchText, isLoadingMore = false) => {
    if (!zid || searchText.length < 3) return;
    try {
      if (!isLoadingMore) {
        setLoading(true);
      }
      const offset = isLoadingMore ? customerOffset + LIMIT : 0;
      const response = await api.get(
        `/customers/all/${zid}?customer=${searchText}&employee_id=${user.user_id}&limit=${LIMIT}&offset=${offset}`
      );
      const newCustomers = response.data || [];
      if (!isLoadingMore) {
        setCustomers(newCustomers);
      } else {
        setCustomers([...customers, ...newCustomers]);
      }
      setHasMoreCustomers(newCustomers.length === LIMIT);
      setCustomerOffset(offset);
    } catch (error) {
      console.error("Error searching customers:", error);
      if (!isLoadingMore) {
        setCustomers([]);
      }
    } finally {
      setLoading(false);
      setLoadingMoreCustomers(false);
    }
  };

  const searchItems = async (searchText, isLoadingMore = false) => {
    if (!zid || searchText.length < 3) return;
    try {
      if (!isLoadingMore) {
        setItemsLoading(true);
      }
      const offset = isLoadingMore ? itemOffset + LIMIT : 0;
      const response = await api.get(
        `/items/all/${zid}?item_name=${searchText}&limit=${LIMIT}&offset=${offset}`
      );
      const newItems = response.data || [];
      if (!isLoadingMore) {
        setItems(newItems);
      } else {
        setItems([...items, ...newItems]);
      }
      setHasMoreItems(newItems.length === LIMIT);
      setItemOffset(offset);
    } catch (error) {
      console.error("Error searching items:", error);
      if (!isLoadingMore) {
        setItems([]);
      }
    } finally {
      setItemsLoading(false);
      setLoadingMoreItems(false);
    }
  };

  const handleLoadMoreCustomers = () => {
    if (!loadingMoreCustomers && hasMoreCustomers && customerSearchText.length >= 3) {
      setLoadingMoreCustomers(true);
      searchCustomers(customerSearchText, true);
    }
  };

  const handleLoadMoreItems = () => {
    if (!loadingMoreItems && hasMoreItems && itemSearchText.length >= 3) {
      setLoadingMoreItems(true);
      searchItems(itemSearchText, true);
    }
  };

  const handleZidSelect = (selectedZid) => {
    setZid(selectedZid);
    setShowZidSheet(false);
    // Reset customer and item when ZID changes
    setCustomer("");
    setCustomerName("");
    setCustomerAddress("");
    setItem("");
    setItemName("");
    setItemPrice(0);
    setQuantity("");
    // Clear cart if ZID changes
    setCartItems([]);
    AsyncStorage.removeItem("cartItem");
  };

  const handleCustomerSelect = (selectedCustomer) => {
    setCustomer(selectedCustomer.xcus);
    setCustomerName(selectedCustomer.xorg);
    setCustomerAddress(selectedCustomer.xadd1);
    setShowCustomerSheet(false);
  };

  const handleItemSelect = (selectedItem) => {
    setItem(selectedItem.item_id);
    setItemName(selectedItem.item_name);
    setItemPrice(selectedItem.std_price);
    setShowItemSheet(false);
  };

  const addToCart = async () => {
    if (!zid || !customer || !item || !quantity) return;

    const newItem = {
      xitem: item,
      xdesc: itemName,
      xqty: parseInt(quantity),
      xprice: itemPrice,
      xroword: cartItems.length + 1,
      xdate: new Date().toISOString().split('T')[0],
      xsl: Math.random().toString(36).substring(7),
      xlat: null,
      xlong: null,
      xlinetotal: parseInt(quantity) * itemPrice
    };

    // Check if item already exists
    const existingItemIndex = cartItems.findIndex(i => i.xitem === item);
    let updatedItems;

    if (existingItemIndex >= 0) {
      // Update existing item
      updatedItems = cartItems.map((item, index) =>
        index === existingItemIndex ? { ...item, xqty: parseInt(quantity), xlinetotal: parseInt(quantity) * itemPrice } : item
      );
    } else {
      // Add new item
      updatedItems = [...cartItems, newItem];
    }

    setCartItems(updatedItems);

    // Save to AsyncStorage
    const cartData = {
      zid: zid,
      xcus: customer,
      xcusname: customerName,
      xcusadd: customerAddress,
      items: updatedItems
    };

    try {
      await AsyncStorage.setItem("cartItem", JSON.stringify(cartData));
    } catch (error) {
      console.error("Error saving cart:", error);
    }

    // Reset item fields
    setItem("");
    setItemName("");
    setItemPrice(0);
    setQuantity("");
  };

  const removeFromCart = async (itemToRemove) => {
    const updatedItems = cartItems.filter(item => item.xitem !== itemToRemove.xitem);
    setCartItems(updatedItems);

    // Update AsyncStorage
    const cartData = {
      zid: zid,
      xcus: customer,
      xcusname: customerName,
      xcusadd: customerAddress,
      items: updatedItems
    };

    try {
      if (updatedItems.length === 0) {
        await AsyncStorage.removeItem("cartItem");
      } else {
        await AsyncStorage.setItem("cartItem", JSON.stringify(cartData));
      }
    } catch (error) {
      console.error("Error updating cart:", error);
    }
  };

  const addOrder = async () => {
    if (!cartItems.length) return;

    try {
      // Save to orders in AsyncStorage
      const existingOrders = await AsyncStorage.getItem("orders");
      const orders = existingOrders ? JSON.parse(existingOrders) : { orders: [] };

      orders.orders.push({
        zid: zid,
        xcus: customer,
        xcusname: customerName,
        xcusadd: customerAddress,
        items: cartItems
      });

      await AsyncStorage.setItem("orders", JSON.stringify(orders));

      // Clear cart
      await AsyncStorage.removeItem("cartItem");
      setCartItems([]);
      setZid("");
      setCustomer("");
      setCustomerName("");
      setCustomerAddress("");

    } catch (error) {
      console.error("Error saving order:", error);
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((sum, item) => sum + item.xlinetotal, 0);
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView>
        <Box className="p-4">
          

          <VStack space="lg">
            {/* ZID Selection */}
            <Box>
              <Text className="text-gray-600 mb-2">Business ZID</Text>
              <Button
                variant="outline"
                className="w-full"
                onPress={() => setShowZidSheet(true)}
                disabled={cartItems.length > 0}
              >
                <ButtonText>{zid || "Select ZID"}</ButtonText>
                <ButtonIcon as={ChevronDown} />
              </Button>
            </Box>

            {/* Customer Selection */}
            <Box>
              <Text className="text-gray-600 mb-2">Customer</Text>
              <Button
                variant="outline"
                className="w-full"
                onPress={() => setShowCustomerSheet(true)}
                disabled={!zid || cartItems.length > 0}
              >
                <ButtonText>{customerName || "Select Customer"}</ButtonText>
                <ButtonIcon as={ChevronDown} />
              </Button>
            </Box>

            {/* Item Selection */}
            <Box>
              <Text className="text-gray-600 mb-2">Item</Text>
              <Button
                variant="outline"
                className="w-full"
                onPress={() => setShowItemSheet(true)}
                disabled={!zid || !customer}
              >
                <ButtonText>{itemName || "Select Item"}</ButtonText>
                <ButtonIcon as={ChevronDown} />
              </Button>
            </Box>

            {/* Quantity Input */}
            <Box>
              <Text className="text-gray-600 mb-2">Quantity</Text>
              <Input size="xl">
                <InputField
                  placeholder="Enter quantity"
                  value={quantity}
                  onChangeText={setQuantity}
                  keyboardType="numeric"
                  disabled={!zid || !customer || !item}
                />
              </Input>
            </Box>

            {/* Add to Cart Button */}
            <Button
              onPress={addToCart}
              disabled={!zid || !customer || !item || !quantity}
              className="w-full"
            >
              <ButtonIcon as={ShoppingCart} />
              <ButtonText>Add to Cart</ButtonText>
            </Button>

            {/* Cart Items */}
            {cartItems.length > 0 && (
              <Card className="w-full mt-4 overflow-hidden border-lg shadow-lg">
                <VStack space="md">
                  {/* Enhanced Cart Header */}
                  <Box className="px-6 py-4 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg">
                    <HStack space="3" alignItems="center">
                      <Text className="text-lg font-semibold text-white truncate">
                        {customerName.length > 25 ? customerName.substring(0, 25) + "..." : customerName}
                      </Text>
                    </HStack>
                  </Box>

                  {/* Refined Cart Items */}
                  <VStack space="0" className="px-3 py-3 bg-gray-50/50">
                    {cartItems.map((item, index) => (
                      <Box key={item.xsl} className="group overflow-visible">
                        {index > 0 && <Divider className="my-2 opacity-20" />}
                        <HStack
                          justifyContent="space-between"
                          alignItems="center"
                          className="p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
                        >
                          <VStack space="2" flex={1}>
                            
                            <Text className="text-xs font-bold text-gray-600 italic">
                              Code: {item.xitem}
                            </Text>
                            <Text className="text-base font-semibold text-gray-900">
                              {item.xdesc.length > 30 ? item.xdesc.substring(0, 30) + "..." : item.xdesc}
                            </Text>
                            <HStack space="3" alignItems="center">
                              <Box className="bg-primary-50/80 px-2.5 py-1 rounded-full">
                                <Text className="text-xs font-medium text-primary-800">
                                  Qty: {item.xqty}
                                </Text>
                              </Box>
                              <Text className="text-gray-400">•</Text>
                              <Box className="bg-green-50 px-2.5 py-1 rounded-full">
                                <Text className="text-xs font-medium text-green-800">
                                  ৳{item.xprice}
                                </Text>
                              </Box>
                              <Text className="text-gray-400">→</Text>
                              <Box className="bg-purple-50 px-2.5 py-1 rounded-full">
                                <Text className="text-xs font-bold text-purple-900">
                                  ৳{item.xlinetotal}
                                </Text>
                              </Box>
                            </HStack>
                          </VStack>

                          {/* Align delete button to the right without gray background */}
                          <Button
                            variant="ghost"
                            action="error"

                            onPress={() => removeFromCart(item)}
                            className="opacity-80 hover:opacity-100 active:scale-95 transition-all ml-auto border-none bg-primary-50/0 group-hover:bg-primary-50/20"
                          >
                            <ButtonIcon as={Trash2} size="md" className="text-red-600" />
                          </Button>
                        </HStack>
                      </Box>
                    ))}
                  </VStack>

                  {/* Improved Cart Footer */}
                  <Box className="px-3 py-3 bg-gradient-to-r from-gray-100 to-gray-300 border-t border-gray-200 rounded-lg">
                    <HStack justifyContent="space-between" alignItems="center">
                      <VStack space="1">

                        <Box className="bg-primary-50/80 px-2.5 py-1 rounded-full">
                          <Text className="text-xs font-medium text-primary-800">
                            {cartItems.length} {cartItems.length === 1 ? 'Item' : 'Items'}
                          </Text>
                        </Box>
                        <Text className="text-xs font-medium text-gray-600">
                          Total Amount
                        </Text>
                        <Text className="text-xl font-extrabold text-gray-900">
                          ৳{calculateTotal()}
                        </Text>

                      </VStack>

                    </HStack>
                  </Box>
                </VStack>
              </Card>
            )}

            {/* Add Order Button */}
            {cartItems.length > 0 && (
              <Button
                size="lg"
                className="w-full mt-4"
                onPress={addOrder}
              >
                <ButtonText>Add Order</ButtonText>
              </Button>
            )}
          </VStack>
        </Box>
      </ScrollView>

      {/* ZID Selection Drawer */}
      <Drawer
        isOpen={showZidSheet}
        onClose={() => setShowZidSheet(false)}
        size="full"
        anchor="bottom"
      >
        <DrawerBackdrop />
        <DrawerContent className="bg-gray-50">
          <DrawerHeader className="flex-row items-center justify-between px-4 py-3 bg-white border-b border-gray-100">
            <VStack>
              <Text className="text-xs text-gray-500 uppercase tracking-wider">Select Business</Text>
              <Heading size="lg" className="text-primary-900">Available ZIDs</Heading>
            </VStack>
            <Button
              variant="link"
              onPress={() => setShowZidSheet(false)}
              className="p-2"
            >
              <ButtonIcon as={X} size="lg" className="text-gray-400" />
            </Button>
          </DrawerHeader>
          <DrawerBody>
            <ScrollView className="flex-1 px-4 py-2">
              <VStack space="3">
                {zids.map((id) => (
                  <Button
                    key={id}
                    variant="link"
                    onPress={() => handleZidSelect(id)}
                    className="w-full p-0 m-0"
                  >
                    <Card className="w-full w-full bg-white border-0 shadow-sm hover:bg-gray-50 active:bg-gray-50">
                      <Box className="p-3">
                        <HStack space="2" alignItems="center">
                          <Text className="text-sm font-medium text-gray-900">ZID:</Text>
                          <Text className="text-[11px] px-2 py-1 bg-primary-50 text-primary-700 rounded-full">{id}</Text>
                        </HStack>
                      </Box>
                    </Card>
                  </Button>
                ))}
              </VStack>
            </ScrollView>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Customer Selection Drawer */}
      <Drawer
        isOpen={showCustomerSheet}
        onClose={() => setShowCustomerSheet(false)}
        size="full"
        anchor="bottom"
      >
        <DrawerBackdrop />
        <DrawerContent className="bg-gray-50">
          <DrawerHeader className="flex-row items-center justify-between px-4 py-3 bg-white border-b border-gray-100">
            <VStack>
              <Text className="text-xs text-gray-500 uppercase tracking-wider">Selected Business</Text>
              <Heading size="lg" className="text-primary-900">ZID {zid}</Heading>
            </VStack>
            <Button
              variant="link"
              onPress={() => setShowCustomerSheet(false)}
              className="p-2"
            >
              <ButtonIcon as={X} size="lg" className="text-gray-400" />
            </Button>
          </DrawerHeader>
          <DrawerBody>
            {/* Sticky Search Box with Frosted Glass Effect */}
            <Box className="sticky top-0 z-10">
              <Box className="backdrop-blur-lg bg-white/90 px-4 py-3 shadow-sm border-b border-gray-100">
                <Input
                  size="md"
                  className="bg-gray-50/80 border border-gray-100 rounded-xl"
                >
                  <InputField
                    placeholder="Search customers..."
                    value={customerSearchText}
                    onChangeText={(text) => {
                      setCustomerSearchText(text);
                      if (text.length >= 3) {
                        searchCustomers(text);
                      } else {
                        setCustomers([]);
                      }
                    }}
                    className="text-sm"
                  />
                  <InputSlot px="$3">
                    <InputIcon as={Search} size={18} className="text-gray-400" />
                  </InputSlot>
                </Input>
              </Box>
            </Box>

            {/* Content with Elegant Cards */}
            <ScrollView
              className="flex-1 px-4"
              onScroll={({ nativeEvent }) => {
                const { layoutMeasurement, contentOffset, contentSize } = nativeEvent;
                const paddingToBottom = 20;
                if (layoutMeasurement.height + contentOffset.y >=
                  contentSize.height - paddingToBottom) {
                  handleLoadMoreCustomers();
                }
              }}
              scrollEventThrottle={400}
            >
              {loading ? (
                <Box className="py-8 flex items-center justify-center">
                  <HStack space="sm" alignItems="center">
                    <Spinner size="small" color="$primary500" />
                    <Text size="sm" className="text-gray-600 font-medium">Searching customers...</Text>
                  </HStack>
                </Box>
              ) : customers.length === 0 ? (
                <Box className="py-8">
                  <Text className="text-center text-sm text-gray-500">
                    {customerSearchText.length < 3
                      ? "Type at least 3 characters to search"
                      : "No customers found"}
                  </Text>
                </Box>
              ) : (
                <VStack space="4" className="py-3 pb-20 min-h-screen">
                  {customers.map((cust) => (
                    <Button
                      key={cust.xcus}
                      variant="link"
                      onPress={() => handleCustomerSelect(cust)}
                      className="w-full p-0 m-0"
                    >
                      <Card className="w-full bg-white border-0 shadow-sm active:bg-gray-50/80 hover:border hover:border-primary-100 rounded-2xl overflow-hidden transition-all duration-200">
                        <Box className="p-5">
                          <VStack space="6">
                            <Box className="bg-gray-50 rounded-xl px-4 py-3 border border-gray-100">
                              <HStack space="3" alignItems="center">
                                <Box className="bg-blue-50 border border-blue-100 rounded-lg px-3 py-1.5">
                                  <Text className="text-xs font-semibold text-blue-700 tracking-wider">{cust.xcus}</Text>
                                </Box>
                                <Box className="bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-1.5">
                                  <Text className="text-xs font-semibold text-emerald-700 tracking-wider">{cust.xcity}</Text>
                                </Box>
                              </HStack>
                            </Box>

                            <VStack space="4">
                              <VStack space="1">
                                <Text className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Customer Name</Text>
                                <Text className="text-base font-semibold text-gray-800 leading-snug">{cust.xorg}</Text>
                              </VStack>

                              <VStack space="1">
                                <Text className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Location</Text>
                                <Text className="text-sm text-gray-600 leading-relaxed">{cust.xadd1}</Text>
                              </VStack>
                            </VStack>
                          </VStack>
                        </Box>
                      </Card>
                    </Button>
                  ))}
                  {loadingMoreCustomers && (
                    <Box className="py-6 flex items-center justify-center">
                      <HStack space="sm" alignItems="center" className="bg-white/80 px-4 py-2 rounded-full shadow-sm">
                        <Spinner size="small" color="$primary500" />
                        <Text size="xs" className="text-gray-600 font-medium">Loading more...</Text>
                      </HStack>
                    </Box>
                  )}
                </VStack>
              )}
            </ScrollView>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Item Selection Drawer */}
      <Drawer
        isOpen={showItemSheet}
        onClose={() => setShowItemSheet(false)}
        size="full"
        anchor="bottom"
      >
        <DrawerBackdrop />
        <DrawerContent className="bg-gray-50">
          <DrawerHeader className="flex-row items-center justify-between px-4 py-3 bg-white border-b border-gray-100">
            <VStack>
              <Text className="text-xs text-gray-500 uppercase tracking-wider">Selected Business</Text>
              <Heading size="lg" className="text-primary-900">ZID {zid}</Heading>
            </VStack>
            <Button
              variant="link"
              onPress={() => setShowItemSheet(false)}
              className="p-2"
            >
              <ButtonIcon as={X} size="lg" className="text-gray-400" />
            </Button>
          </DrawerHeader>
          <DrawerBody>
            {/* Sticky Search Box with Frosted Glass Effect */}
            <Box className="sticky top-0 z-10">
              <Box className="backdrop-blur-lg bg-white/90 px-4 py-3 shadow-sm border-b border-gray-100">
                <Input
                  size="md"
                  className="bg-gray-50/80 border border-gray-100 rounded-xl"
                >
                  <InputField
                    placeholder="Search items..."
                    value={itemSearchText}
                    onChangeText={(text) => {
                      setItemSearchText(text);
                      if (text.length >= 3) {
                        searchItems(text);
                      } else {
                        setItems([]);
                      }
                    }}
                    className="text-sm"
                  />
                  <InputSlot px="$3">
                    <InputIcon as={Search} size={18} className="text-gray-400" />
                  </InputSlot>
                </Input>
              </Box>
            </Box>

            {/* Content with Elegant Cards */}
            <ScrollView
              className="flex-1 px-4"
              onScroll={({ nativeEvent }) => {
                const { layoutMeasurement, contentOffset, contentSize } = nativeEvent;
                const paddingToBottom = 20;
                if (layoutMeasurement.height + contentOffset.y >=
                  contentSize.height - paddingToBottom) {
                  handleLoadMoreItems();
                }
              }}
              scrollEventThrottle={400}
            >
              {itemsLoading ? (
                <Box className="py-8 flex items-center justify-center">
                  <HStack space="sm" alignItems="center">
                    <Spinner size="small" color="$primary500" />
                    <Text size="sm" className="text-gray-600 font-medium">Searching items...</Text>
                  </HStack>
                </Box>
              ) : items.length === 0 ? (
                <Box className="py-8">
                  <Text className="text-center text-sm text-gray-500">
                    {itemSearchText.length < 3
                      ? "Type at least 3 characters to search"
                      : "No items found"}
                  </Text>
                </Box>
              ) : (
                <VStack space="4" className="py-2 pb-20 w-full my-[40px]">
                  {items.map((itm) => (
                    <Box key={itm.item_id} className="w-full min-h-[140px]">
                      <Button
                        variant="link"
                        onPress={() => handleItemSelect(itm)}
                        className="w-full p-0 m-0"
                      >
                        <Card className="w-full bg-white border-0 shadow-sm active:bg-gray-50/80 hover:border hover:border-primary-100 rounded-xl transition-all duration-200">
                          <Box className="p-1">
                            <VStack space="1">
                              <Box className="bg-gray-50 rounded-lg px-2 py-0.5 border border-gray-100">
                                <Box className="bg-blue-50 border border-blue-100 self-start rounded-md px-1.5 py-0.5">
                                  <Text className="text-[9px] font-semibold text-blue-700 tracking-wider">{itm.item_id}</Text>
                                </Box>
                              </Box>

                              <VStack space="1">
                                <VStack space="0">
                                  <Text className="text-[9px] font-medium text-gray-400 uppercase tracking-wider">Item Name</Text>
                                  <Text className="text-xs font-semibold text-gray-800 leading-snug">{itm.item_name}</Text>
                                </VStack>

                                <Box className="bg-gray-50 rounded-lg px-2 py-0.5 border border-gray-100">
                                  <HStack space="2" alignItems="center" justifyContent="space-between">
                                    <Box className="bg-primary-100 border border-tertiary-800 rounded-md px-1.5 py-0.5">
                                      <Text className="text-[10px] font-bold text-primary-800">৳{itm.std_price}</Text>
                                    </Box>
                                    <Box className="bg-amber-50 border border-amber-100 rounded-md px-1.5 py-0.5">
                                      <Text className="text-[9px] font-medium text-amber-700">Stock: {itm.stock || 0}</Text>
                                    </Box>
                                  </HStack>
                                </Box>
                              </VStack>
                            </VStack>
                          </Box>
                        </Card>
                      </Button>
                    </Box>
                  ))}
                  {loadingMoreItems && (
                    <Box className="py-2 flex items-center justify-center">
                      <HStack space="sm" alignItems="center" className="bg-white/80 px-2 py-1 rounded-full shadow-sm">
                        <Spinner size="small" color="$primary500" />
                        <Text size="xs" className="text-gray-600 font-medium">Loading more...</Text>
                      </HStack>
                    </Box>
                  )}
                </VStack>
              )}
            </ScrollView>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </SafeAreaView>
  );
}