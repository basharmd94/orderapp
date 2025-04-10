import React, { useState, useCallback, useEffect, useRef, memo } from 'react';
import { View, FlatList, TouchableOpacity, Keyboard } from 'react-native';
import { Input, InputField, InputIcon, InputSlot } from '@/components/ui/input';
import { ChevronDown, Search, X, ShoppingCart, CreditCard, ShoppingBasket } from 'lucide-react-native';
import { Spinner } from '@/components/ui/spinner';
import {
  Drawer,
  DrawerBackdrop,
  DrawerContent,
  DrawerHeader,
  DrawerBody,
} from '@/components/ui/drawer';
import { Text } from '@/components/ui/text';
import { Button, ButtonIcon, ButtonText } from '@/components/ui/button';
import { Heading } from '@/components/ui/heading';
import { VStack } from '@/components/ui/vstack';
import { Box } from '@/components/ui/box';
import { debounce } from 'lodash';

// Memoize ItemCard to prevent unnecessary re-renders
const ItemCard = memo(({ item, onSelect }) => (
  <TouchableOpacity
    onPress={onSelect}
    activeOpacity={0.7}
    className="mx-4 my-2"
  >
    <View className="bg-white rounded-2xl border border-gray-200 shadow-lg p-4">
      <View className="flex-row items-center">
        <View className="bg-warning-50 p-3 rounded-xl mr-3">
          <ShoppingCart size={20} className="text-warning-500" />
        </View>
        <View className="flex-1">
          <Text className="text-lg font-semibold text-gray-900" numberOfLines={1} ellipsizeMode="tail">
            {item.item_name}
          </Text>
          <Text className="text-sm text-gray-600 mt-1">
            ID: {item.item_id}
          </Text>
        </View>
      </View>

      <View className="h-px bg-gray-200 my-3" />

      <View className="flex-row justify-between mt-1">
        <View className="flex-row items-center flex-1">
          <ShoppingBasket size={16} color="#666666" />
          <Text className="ml-2 text-sm text-gray-600" numberOfLines={1} ellipsizeMode="tail">
            Stock: {item.stock || 'No stock info'}
          </Text>
        </View>
        <View className="flex-row items-center flex-1">
          <CreditCard size={16} color="#666666" />
          <Text className="ml-2 text-sm text-gray-600" numberOfLines={1} ellipsizeMode="tail">
            Price: ৳{item.std_price || 'Not available'}
          </Text>
        </View>
      </View>
    </View>
  </TouchableOpacity>
));

export default function ItemSelector({
  zid,
  itemName,
  disabled,
  showItemSheet,
  setShowItemSheet,
  onItemSelect,
  items,
  loading,
  searchText,
  setSearchText,
  onSearch
}) {
  const drawerInputRef = useRef(null);
  const [localSearchText, setLocalSearchText] = useState('');
  const initialSearchDoneRef = useRef(false);
  
  // Create debounced search function
  const debouncedSearch = useCallback(
    debounce((text) => {
      setSearchText(text);
      if (text.length >= 1) {
        onSearch(text);
      } else {
        // Clear items when search is empty
        setSearchText('');
        onSearch('');
      }
    }, 400),
    [setSearchText, onSearch]
  );

  const handleSearchChange = useCallback((text) => {
    setLocalSearchText(text);
    debouncedSearch(text);
  }, [debouncedSearch]);

  // Clean up debounce on unmount
  useEffect(() => {
    return () => {
      debouncedSearch.cancel?.();
    };
  }, [debouncedSearch]);

  // Sync localSearchText with searchText when the drawer opens
  useEffect(() => {
    if (showItemSheet) {
      setLocalSearchText(searchText || '');
      
      // Only trigger search on initial open if searchText exists
      if (searchText?.length >= 1 && !initialSearchDoneRef.current) {
        initialSearchDoneRef.current = true;
        // Use timeout to prevent immediate search that could cause update loop
        setTimeout(() => {
          onSearch(searchText);
        }, 0);
      }
    } else {
      // Reset flag when drawer closes
      initialSearchDoneRef.current = false;
    }
  }, [showItemSheet, searchText, onSearch]);

  const handleClearSearch = useCallback(() => {
    setLocalSearchText('');
    setSearchText('');
    onSearch('');
  }, [setSearchText, onSearch]);

  const renderItem = useCallback(({ item }) => (
    <ItemCard
      item={item}
      onSelect={() => {
        onItemSelect(item);
        setShowItemSheet(false);
        Keyboard.dismiss();
      }}
    />
  ), [onItemSelect, setShowItemSheet]);

  const getItemKey = useCallback((item) => 
    `item-${item.item_id}-${zid}`, 
  [zid]);

  return (
    <VStack space="md">
      <Button
        variant="outline"
        className="border border-primary-50 rounded-2xl flex-row items-center justify-between"
        onPress={() => setShowItemSheet(true)}
        disabled={disabled}
      >
        <ButtonText className="text-primary-200 text-xs">
          {itemName || "Select Item"}
        </ButtonText>
        <ButtonIcon as={ChevronDown} className="text-primary-50" />
      </Button>

      <Drawer
        isOpen={showItemSheet}
        onClose={() => {
          setShowItemSheet(false);
          Keyboard.dismiss();
        }}
        size="full"
        anchor="bottom"
      >
        <DrawerBackdrop />
        <DrawerContent className="h-full">
          <DrawerHeader className="bg-white border-b border-gray-100">
            <View className="p-4">
              <Text className="text-xs text-gray-600 uppercase mb-1">Select Item from</Text>
              <View className="flex-row justify-between items-center">
                <Heading size="lg">Business</Heading>
                <View className="bg-orange-400 px-2 py-1 rounded-lg">
                  <Text className="text-white font-semibold">ZID {zid}</Text>
                </View>
              </View>

              <Box className="mt-4 w-[280px]">
                <View className="relative">
                  <Input
                    size="sm"
                    className="bg-white border border-gray-200 rounded-xl w-full h-10"
                  >
                    <InputField
                      ref={drawerInputRef}
                      placeholder={`Search items in ZID ${zid}...`}
                      value={localSearchText}
                      onChangeText={handleSearchChange}
                      className="text-sm"
                      autoCorrect={false}
                      spellCheck={false}
                      autoCapitalize="none"
                      returnKeyType="search"
                    />
                    <InputSlot px="$3">
                      {localSearchText ? (
                        <TouchableOpacity 
                          onPress={handleClearSearch}
                          hitSlop={{ top: 10, right: 10, bottom: 10, left: 10 }}
                        >
                          <InputIcon as={X} size={18} className="text-gray-400" />
                        </TouchableOpacity>
                      ) : (
                        <InputIcon as={Search} size={18} className="text-gray-400" />
                      )}
                    </InputSlot>
                  </Input>
                </View>
              </Box>
            </View>
          </DrawerHeader>

          <View style={{ flex: 1 }} className="bg-gray-100">
            <FlatList
              data={items}
              renderItem={renderItem}
              keyExtractor={getItemKey}
              ListEmptyComponent={
                <View className="py-5 items-center">
                  <Text className="text-gray-600 text-center">
                    {localSearchText.length < 1
                      ? "Type at least 1 character to search"
                      : loading
                      ? "Searching..."
                      : "No items found"}
                  </Text>
                </View>
              }
              removeClippedSubviews={true}
              initialNumToRender={10}
              maxToRenderPerBatch={10}
              updateCellsBatchingPeriod={50}
              windowSize={11}
              keyboardShouldPersistTaps="handled"
              keyboardDismissMode="on-drag"
              style={{ flex: 1 }}
              contentContainerStyle={{ 
                flexGrow: items.length === 0 ? 1 : undefined,
                paddingTop: 8,
                paddingBottom: 20 
              }}
            />
          </View>
        </DrawerContent>
      </Drawer>
    </VStack>
  );
}
