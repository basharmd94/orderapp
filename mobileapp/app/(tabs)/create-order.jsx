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
import { useState, useEffect, useRef, useCallback } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import api from "@/lib/api";
import { Fab, FabLabel, FabIcon } from "@/components/ui/fab";
import { Plus, ShoppingCart } from "lucide-react-native";
import { Spinner } from "@/components/ui/spinner";
import { useOrderStore } from "@/stores/orderStore";

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
  const [customerOffset, setCustomerOffset] = useState(0);
  const [itemOffset, setItemOffset] = useState(0);
  const [loadingMoreCustomers, setLoadingMoreCustomers] = useState(false);
  const [loadingMoreItems, setLoadingMoreItems] = useState(false);
  const [hasMoreCustomers, setHasMoreCustomers] = useState(true);
  const [hasMoreItems, setHasMoreItems] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  const LIMIT = 10;
  const searchSequence = useRef(0);
  const itemSearchSequence = useRef(0);
  const searchDebounceRef = useRef(null);
  const itemSearchDebounceRef = useRef(null);
  const activeSearchRef = useRef(false);
  const searchTimeoutRef = useRef(null);
  const lastSearchRef = useRef('');
  const SEARCH_DELAY = 500; // 500ms delay between searches
  const abortControllerRef = useRef(null);
  const INITIAL_SEARCH_DELAY = 800; // Longer delay for initial search
  const TYPING_DELAY = 500; // Medium delay while typing
  const LOAD_MORE_DELAY = 300; // Short delay for loading more

  useEffect(() => {
    loadCartItems();
  }, []);

  useEffect(() => {
    searchSequence.current = 0;
    setCustomerOffset(0);
    setHasMoreCustomers(true);
    if (customerSearchText.length < 3) { // Changed from 3 to 1
      setCustomers([]);
      setHasMoreCustomers(false);
    }
  }, [customerSearchText]);

  useEffect(() => {
    itemSearchSequence.current = 0;
    setItemOffset(0);
    setHasMoreItems(true);
    if (itemSearchText.length < 3) {
      setItems([]);
      setHasMoreItems(false);
    }
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

  const handleZidSelect = (selectedZid) => {
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

    const parsedQuantity = parseInt(quantity);
    const lineTotal = parsedQuantity * itemPrice;

    const newItem = {
        xitem: item,
        xdesc: itemName,
        xqty: parsedQuantity,
        xprice: parseFloat(itemPrice),  // Ensure price is float
        xroword: cartItems.length + 1,
        xdate: new Date().toISOString().split('T')[0],
        xsl: Math.random().toString(36).substring(7),
        xlat: null,
        xlong: null,
        xlinetotal: lineTotal  // This will now be a float
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
  };

  const removeFromCart = async (itemToRemove) => {
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
  };

  const addOrder = async () => {
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
      setSubmitting(false);
    }
  };

  const searchCustomers = useCallback(async (searchText, isLoadingMore = false) => {
    if (!zid || searchText.length < 3 || !user) { // Changed from 3 to 1
      setCustomers([]);
      return;
    }
    
    try {
      if (!isLoadingMore) {
        setLoading(true);
        setCustomerOffset(0);
      } else {
        setLoadingMoreCustomers(true);
      }
      
      const offset = isLoadingMore ? customerOffset : 0;
      await new Promise(resolve => setTimeout(resolve, 300)); // Add small delay

      const response = await api.get(
        `/customers/all/${zid}?customer=${searchText}&employee_id=${user?.user_id || ''}&limit=${LIMIT}&offset=${offset}`
      );
      
      const newCustomers = response.data || [];
      
      if (!isLoadingMore) {
        setCustomers(newCustomers);
      } else {
        setCustomers(prev => {
          const existingIds = new Set(prev.map(c => c.xcus));
          const uniqueNewCustomers = newCustomers.filter(c => !existingIds.has(c.xcus));
          return [...prev, ...uniqueNewCustomers];
        });
      }
      
      setHasMoreCustomers(newCustomers.length === LIMIT);
      setCustomerOffset(offset + (newCustomers.length === LIMIT ? LIMIT : 0));
      
    } catch (error) {
      console.error("Error searching customers:", error);
      if (!isLoadingMore) {
        setCustomers([]);
      }
      setHasMoreCustomers(false);
    } finally {
      setLoading(false);
      setLoadingMoreCustomers(false);
    }
  }, [zid, user]);

  // Add effect to clear search results when user is not available
  useEffect(() => {
    if (!user) {
      setCustomers([]);
      setHasMoreCustomers(false);
      setCustomerOffset(0);
    }
  }, [user]);

  const handleCustomerSearch = useCallback((text) => {
    setCustomerSearchText(text);
    
    if (searchDebounceRef.current) {
      clearTimeout(searchDebounceRef.current);
    }

    if (text.length >= 1) { // Changed from 3 to 1
      searchDebounceRef.current = setTimeout(() => {
        searchCustomers(text);
      }, 500);
    } else {
      setCustomers([]);
      setHasMoreCustomers(false);
    }
  }, [searchCustomers]);

  const handleLoadMoreCustomers = useCallback(() => {
    if (!loadingMoreCustomers && hasMoreCustomers && customerSearchText.length >= 1) { // Changed from 3 to 1
      searchCustomers(customerSearchText, true);
    }
  }, [loadingMoreCustomers, hasMoreCustomers, customerSearchText, searchCustomers]);

  // Similar updates for item search
  const searchItems = async (searchText, isLoadingMore = false) => {
    if (!zid || searchText.length < 1) { // Changed from 3 to 1
      setItems([]);
      setHasMoreItems(false);
      return;
    }
    
    try {
      const currentSequence = ++itemSearchSequence.current;
      
      if (!isLoadingMore) {
        setItemsLoading(true);
        setItemOffset(0);
        setItems([]);
      } else if (loadingMoreItems) {
        return;
      } else {
        setLoadingMoreItems(true);
      }
      
      const offset = isLoadingMore ? itemOffset : 0;
      const response = await api.get(
        `/items/all/${zid}?item_name=${searchText}&limit=${LIMIT}&offset=${offset}`
      );

      if (currentSequence !== itemSearchSequence.current) {
        return;
      }
      
      const newItems = response.data || [];
      
      if (!isLoadingMore) {
        setItems(newItems);
      } else {
        const existingIds = new Set(items.map(item => item.item_id));
        const uniqueNewItems = newItems.filter(item => !existingIds.has(item.item_id));
        if (uniqueNewItems.length > 0) {
          setItems(prev => [...prev, ...uniqueNewItems]);
        }
      }
      
      setHasMoreItems(newItems.length === LIMIT);
      if (newItems.length === LIMIT) {
        setItemOffset(offset + LIMIT);
      } else {
        setHasMoreItems(false);
      }
    } catch (error) {
      console.error("Error searching items:", error);
      if (!isLoadingMore) {
        setItems([]);
      }
      setHasMoreItems(false);
    } finally {
      setItemsLoading(false);
      setLoadingMoreItems(false);
    }
  };

  const handleItemSearch = (text) => {
    setItemSearchText(text);
    if (text.length >= 3) { // Changed from 3 to 1
      // Use timeout for all searches
      const timeoutId = setTimeout(() => {
        searchItems(text);
      }, 300);
      return () => clearTimeout(timeoutId);
    } else {
      setItems([]);
      setHasMoreItems(false);
    }
  };

  const handleLoadMoreItems = () => {
    if (!loadingMoreItems && hasMoreItems && itemSearchText.length >= 3) { // Changed from 3 to 1
      searchItems(itemSearchText, true);
    }
  };

  // Cleanup timeouts
  useEffect(() => {
    return () => {
      if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
      if (itemSearchDebounceRef.current) clearTimeout(itemSearchDebounceRef.current);
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    };
  }, []);

  // Reset search state when component unmounts or zid changes
  useEffect(() => {
    lastSearchRef.current = '';
    setCustomers([]);
    setHasMoreCustomers(false);
    setCustomerOffset(0);
    if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
  }, [zid]);

  return (
    <Box className="flex-1 bg-gray-50">
      <SafeAreaView className="flex-1 ">
        <ScrollView>
          <Box className="p-4">
            <VStack space="lg">
              <BusinessSelector
                zid={zid}
                onZidSelect={handleZidSelect}
                disabled={cartItems.length > 0}
                showZidSheet={showZidSheet}
                setShowZidSheet={setShowZidSheet}
              />

              <CustomerSelector
                zid={zid}
                customer={customer}
                customerName={customerName}
                disabled={!zid || cartItems.length > 0}
                showCustomerSheet={showCustomerSheet}
                setShowCustomerSheet={setShowCustomerSheet}
                onCustomerSelect={handleCustomerSelect}
                customers={customers}
                loading={loading}
                loadingMore={loadingMoreCustomers}
                hasMore={hasMoreCustomers}
                searchText={customerSearchText}
                setSearchText={handleCustomerSearch}
                onLoadMore={handleLoadMoreCustomers}
              />

              <ItemSelector
                zid={zid}
                itemName={itemName}
                disabled={!zid || !customer}
                showItemSheet={showItemSheet}
                setShowItemSheet={setShowItemSheet}
                onItemSelect={handleItemSelect}
                items={items}
                loading={itemsLoading}
                loadingMore={loadingMoreItems}
                hasMore={hasMoreItems}
                searchText={itemSearchText}
                setSearchText={handleItemSearch}
                onLoadMore={handleLoadMoreItems}
              />

              <QuantityInput
                quantity={quantity}
                setQuantity={setQuantity}
                disabled={!zid || !customer || !item}
              />

              <CartList
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
          {/* Show Add to Cart FAB only when item and quantity are selected */}
          {(!!item && !!quantity) && (
            <Fab
              size="sm"
              placement="bottom left"
              onPress={addToCart}
              isDisabled={!zid || !customer}
              className="bg-amber-500 active:scale-95 hover:bg-amber-600 min-w-[140px]"
              m={6}
            >
              <ShoppingCart size={16} className = "text-white text-bold"/>
              <FabLabel className="text-white text-sm font-medium">Add to Cart</FabLabel>
            </Fab>
          )}

          {cartItems.length > 0 && (
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
                  <Plus size={16} className = "text-white text-bold"/>
                  <FabLabel className="text-white text-sm font-medium">Add Order</FabLabel>
                </>
              )}
            </Fab>
          )}
        </Box>
      </SafeAreaView>
    </Box>
  );
}