import { SafeAreaView } from "react-native-safe-area-context";
import { Box } from "@/components/ui/box";
import { ScrollView } from "react-native";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import BusinessSelector from "@/components/create-order/BusinessSelector";
import CustomerSelector from "@/components/create-order/CustomerSelector";
import ItemSelector from "@/components/create-order/ItemSelector";
import QuantityInput from "@/components/create-order/QuantityInput";
import CartList from "@/components/create-order/CartList";
import { useAuth } from "@/context/AuthContext";
import { useState, useEffect, useRef, useCallback, memo } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Fab, FabLabel, FabIcon } from "@/components/ui/fab";
import { Plus, ShoppingCart } from "lucide-react-native";
import { Spinner } from "@/components/ui/spinner";
import { useOrderStore } from "@/stores/orderStore";
import { getCustomers } from "@/database/customerModels";
import { getItems } from "@/database/itemModels";

// Memoized selectors to prevent unnecessary re-renders
const MemoizedBusinessSelector = memo(BusinessSelector);
const MemoizedCustomerSelector = memo(CustomerSelector);
const MemoizedItemSelector = memo(ItemSelector);
const MemoizedQuantityInput = memo(QuantityInput);
const MemoizedCartList = memo(CartList);

export default function CreateOrder() {
  const { user } = useAuth();
  const { loadOrders } = useOrderStore();
  const [zid, setZid] = useState("");
  const [customer, setCustomer] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerAddress, setCustomerAddress] = useState("");
  const [item, setItem] = useState("");
  const [itemName, setItemName] = useState("");
  const [itemPrice, setItemPrice] = useState(0);
  const [quantity, setQuantity] = useState("");
  const [cartItems, setCartItems] = useState([]);

  const [showZidSheet, setShowZidSheet] = useState(false);
  const [showCustomerSheet, setShowCustomerSheet] = useState(false);
  const [showItemSheet, setShowItemSheet] = useState(false);
  const [customerSearchText, setCustomerSearchText] = useState("");
  const [itemSearchText, setItemSearchText] = useState("");
  
  const [customers, setCustomers] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  
  const LIMIT = 40; // Increased limit for better search results
  const searchDebounceRef = useRef(null);
  const itemSearchDebounceRef = useRef(null);
  const SEARCH_DELAY = 120;
  const mountedRef = useRef(true);

  // Only load cart items on initial mount, not on tab revisits
  useEffect(() => {
    if (isInitialLoad) {
      loadCartItems();
      setIsInitialLoad(false);
    }
    
    // Cleanup function to handle component unmounting
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Customer search text side effects - memoized
  const handleCustomerSearchTextChange = useCallback(() => {
    if (customerSearchText.length < 2) {
      setCustomers([]);
    }
  }, [customerSearchText]);

  useEffect(() => {
    handleCustomerSearchTextChange();
  }, [handleCustomerSearchTextChange]);

  // Item search text side effects - memoized
  const handleItemSearchTextChange = useCallback(() => {
    if (itemSearchText.length < 2) {
      setItems([]);
    }
  }, [itemSearchText]);

  useEffect(() => {
    handleItemSearchTextChange();
  }, [handleItemSearchTextChange]);

  const loadCartItems = async () => {
    try {
      const storedCart = await AsyncStorage.getItem("cartItem");
      if (storedCart && mountedRef.current) {
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

  const handleZidSelect = useCallback((selectedZid) => {
    setZid(selectedZid);
    setShowZidSheet(false);
    // Reset when ZID changes 
    setCustomer("");
    setCustomerName("");
    setCustomerAddress("");
    setItem("");
    setItemName("");
    setItemPrice(0);
    setQuantity("");
    setCartItems([]);
    AsyncStorage.removeItem("cartItem");
  }, []);

  const handleCustomerSelect = useCallback((selectedCustomer) => {
    setCustomer(selectedCustomer.xcus);
    setCustomerName(selectedCustomer.xorg);
    setCustomerAddress(selectedCustomer.xadd1);
    setShowCustomerSheet(false);
  }, []);

  const handleItemSelect = useCallback((selectedItem) => {
    setItem(selectedItem.item_id);
    setItemName(selectedItem.item_name);
    setItemPrice(selectedItem.std_price);
    setShowItemSheet(false);
  }, []);

  const addToCart = useCallback(async () => {
    if (!zid || !customer || !item || !quantity) return;

    const parsedQuantity = parseInt(quantity);
    const lineTotal = parsedQuantity * itemPrice;

    const newItem = {
        xitem: item,
        xdesc: itemName,
        xqty: parsedQuantity,
        xprice: parseFloat(itemPrice),
        xroword: cartItems.length + 1,
        xdate: new Date().toISOString().split('T')[0],
        xsl: Math.random().toString(36).substring(7),
        xlat: null,
        xlong: null,
        xlinetotal: lineTotal
    };

    let updatedItems;
    const existingItemIndex = cartItems.findIndex(i => i.xitem === item);

    if (existingItemIndex >= 0) {
        updatedItems = cartItems.map((item, index) =>
            index === existingItemIndex ? 
                { ...item, 
                  xqty: parsedQuantity, 
                  xlinetotal: lineTotal 
                } : item
        );
    } else {
        updatedItems = [...cartItems, newItem];
    }

    setCartItems(updatedItems);

    const cartData = {
        zid,
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
  }, [zid, customer, item, quantity, itemName, itemPrice, cartItems, customerName, customerAddress]);

  const removeFromCart = useCallback(async (itemToRemove) => {
    const updatedItems = cartItems.filter(item => item.xitem !== itemToRemove.xitem);
    setCartItems(updatedItems);

    const cartData = {
      zid,
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
  }, [cartItems, zid, customer, customerName, customerAddress]);

  const addOrder = useCallback(async () => {
    if (!cartItems.length) return;

    try {
      setSubmitting(true);
      const existingOrders = await AsyncStorage.getItem("orders");
      const orders = existingOrders ? JSON.parse(existingOrders) : { orders: [] };
      
      orders.orders.push({
        zid,
        xcus: customer,
        xcusname: customerName,
        xcusadd: customerAddress,
        items: cartItems
      });

      await AsyncStorage.setItem("orders", JSON.stringify(orders));
      await AsyncStorage.removeItem("cartItem");
      await loadOrders(); // Load orders in the store after adding new order
      
      // Reset state
      setCartItems([]);
      setZid("");
      setCustomer("");
      setCustomerName("");
      setCustomerAddress("");
    } catch (error) {
      console.error("Error saving order:", error);
    } finally {
      if (mountedRef.current) {
        setSubmitting(false);
      }
    }
  }, [cartItems, zid, customer, customerName, customerAddress, loadOrders]);

  const searchCustomers = useCallback(async (searchText) => {
    if (!zid || searchText.length < 2 || !user) {
      setCustomers([]);
      return;
    }
    
    try {
      setLoading(true);
      
      const results = await getCustomers(zid, searchText, user.user_id, LIMIT, 0);
      const newCustomers = results || [];
      
      if (!mountedRef.current) return;
      
      setCustomers(newCustomers);
    } catch (error) {
      console.error("Error searching customers:", error);
      if (mountedRef.current) {
        setCustomers([]);
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [zid, user]);

  const searchItems = useCallback(async (searchText) => {
    if (!zid || searchText.length < 2) {
      setItems([]);
      return;
    }
    
    try {
      setItemsLoading(true);
      
      const results = await getItems(zid, searchText, LIMIT, 0);
      const newItems = results || [];
      
      if (!mountedRef.current) return;
      
      setItems(newItems);
    } catch (error) {
      console.error("Error searching items:", error);
      if (mountedRef.current) {
        setItems([]);
      }
    } finally {
      if (mountedRef.current) {
        setItemsLoading(false);
      }
    }
  }, [zid]);

  const handleCustomerSearch = useCallback((text) => {
    setCustomerSearchText(text);
    
    if (searchDebounceRef.current) {
      clearTimeout(searchDebounceRef.current);
    }

    if (text.length >= 1) {
      searchDebounceRef.current = setTimeout(() => {
        searchCustomers(text);
      }, SEARCH_DELAY);
    } else {
      setCustomers([]);
    }
  }, [searchCustomers]);

  const handleItemSearch = useCallback((text) => {
    setItemSearchText(text);
    if (itemSearchDebounceRef.current) {
      clearTimeout(itemSearchDebounceRef.current);
    }

    if (text.length >= 1) {
      itemSearchDebounceRef.current = setTimeout(() => {
        searchItems(text);
      }, SEARCH_DELAY);
    } else {
      setItems([]);
    }
  }, [searchItems]);

  // Cleanup timeouts
  useEffect(() => {
    return () => {
      if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
      if (itemSearchDebounceRef.current) clearTimeout(itemSearchDebounceRef.current);
    };
  }, []);

  // Reset search state when zid changes
  useEffect(() => {
    setCustomers([]);
    setCustomerSearchText('');
    if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
  }, [zid]);

  // FAB rendering memoization to prevent unnecessary rerenders
  const renderAddToCartFab = useCallback(() => {
    if (item && quantity) {
      return (
        <Fab
          size="sm"
          placement="bottom left"
          onPress={addToCart}
          isDisabled={!zid || !customer}
          className="bg-amber-500 active:scale-95 hover:bg-amber-600 min-w-[140px]"
          m={6}
        >
          <ShoppingCart size={16} className="text-white text-bold"/>
          <FabLabel className="text-white text-sm font-medium">Add to Cart</FabLabel>
        </Fab>
      );
    }
    return null;
  }, [item, quantity, addToCart, zid, customer]);

  const renderAddOrderFab = useCallback(() => {
    if (cartItems.length > 0) {
      return (
        <Fab
          size="sm"
          placement="bottom right"
          onPress={addOrder}
          isDisabled={submitting}
          className="bg-emerald-500 active:scale-95 hover:bg-emerald-600 min-w-[140px]"
          m={6}
        >
          {submitting ? (
            <HStack space="sm" alignItems="center" justifyContent="center" className="w-full">
              <Spinner size="small" color="$white" />
              <FabLabel className="text-white text-sm font-medium">Adding...</FabLabel>
            </HStack>
          ) : (
            <>
              <Plus size={16} className="text-white text-bold"/>
              <FabLabel className="text-white text-sm font-medium">Add Order</FabLabel>
            </>
          )}
        </Fab>
      );
    }
    return null;
  }, [cartItems.length, addOrder, submitting]);

  return (
    <Box className="flex-1 bg-gray-50">
      <SafeAreaView className="flex-1">
        <ScrollView removeClippedSubviews={true}>
          <Box className="p-4">
            <VStack space="lg">
              <MemoizedBusinessSelector
                zid={zid}
                onZidSelect={handleZidSelect}
                disabled={cartItems.length > 0}
                showZidSheet={showZidSheet}
                setShowZidSheet={setShowZidSheet}
              />

              <MemoizedCustomerSelector
                zid={zid}
                customer={customer}
                customerName={customerName}
                disabled={!zid || cartItems.length > 0}
                showCustomerSheet={showCustomerSheet}
                setShowCustomerSheet={setShowCustomerSheet}
                onCustomerSelect={handleCustomerSelect}
                customers={customers}
                loading={loading}
                searchText={customerSearchText}
                setSearchText={handleCustomerSearch}
                onSearch={searchCustomers}
              />

              <MemoizedItemSelector
                zid={zid}
                itemName={itemName}
                disabled={!zid || !customer}
                showItemSheet={showItemSheet}
                setShowItemSheet={setShowItemSheet}
                onItemSelect={handleItemSelect}
                items={items}
                loading={itemsLoading}
                searchText={itemSearchText} 
                setSearchText={handleItemSearch}
                onSearch={searchItems}
              />

              <MemoizedQuantityInput
                quantity={quantity}
                setQuantity={setQuantity}
                disabled={!zid || !customer || !item}
              />

              <MemoizedCartList
                cartItems={cartItems}
                customerName={customerName}
                onRemoveItem={removeFromCart}
              />
              
              {/* Add padding at bottom to ensure content is visible above FABs */}
              <Box className="h-16" />
            </VStack>
          </Box>
        </ScrollView>

        {/* FABs */}
        <Box className="absolute bottom-0 left-0 right-0 flex-row justify-between z-50">
          {renderAddToCartFab()}
          {renderAddOrderFab()}
        </Box>
      </SafeAreaView>
    </Box>
  );
}