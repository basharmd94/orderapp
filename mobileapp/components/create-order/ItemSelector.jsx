import React, { useState, useCallback, useEffect, useRef } from 'react';
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

const ItemCard = ({ item, onSelect }) => (
  <TouchableOpacity
    onPress={onSelect}
    activeOpacity={0.7}
    className="mx-4 my-2"
  >
    <View className="bg-white rounded-2xl border border-gray-200 shadow-lg p-4">
      <View className="flex-row items-center">
        <View className="bg-warning-50 p-3 rounded-xl mr-3">
          <ShoppingCart size={20} className = "text-warning-500" />
        </View>
        <View className="flex-1">
          <Text className="text-lg font-semibold text-gray-900">
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
          <Text className="ml-2 text-sm text-gray-600">

            Stock: {item.stock || 'No stock info'}
          </Text>
        </View>
        <View className="flex-row items-center flex-1">
          <CreditCard size={16} color="#666666" />
          <Text className="ml-2 text-sm text-gray-600">
            Price: ৳{item.std_price || 'Not available'}
          </Text>
        </View>
      </View>
    </View>
  </TouchableOpacity>
);

export default function ItemSelector({
  zid,
  itemName,
  disabled,
  showItemSheet,
  setShowItemSheet,
  onItemSelect,
  items,
  loading,
  loadingMore,
  searchText,
  setSearchText,
  onLoadMore,
  hasMoreItems
}) {
  const inputRef = useRef(null);
  const drawerInputRef = useRef(null);
  const [isFocused, setIsFocused] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const loadingTimeoutRef = useRef(null);
  const isTypingRef = useRef(false);
  const scrollOffset = useRef(0);
  const onEndReachedCalledDuringMomentum = useRef(false);
  const isLoadingMoreRef = useRef(false);

  const handleSearchChange = useCallback((text) => {
    setSearchText(text);
    isTypingRef.current = true;
  }, [setSearchText]);

  const handleLoadMore = useCallback(() => {
    if (onEndReachedCalledDuringMomentum.current) return;
    
    if (!loading && 
        !loadingMore && 
        hasMoreItems && 
        searchText.length >= 1 && // Changed from 3 to 1
        !isLoadingMoreRef.current && 
        scrollOffset.current > 0) {
      isLoadingMoreRef.current = true;
      onLoadMore();
      onEndReachedCalledDuringMomentum.current = true;
    }
  }, [loading, loadingMore, hasMoreItems, searchText, onLoadMore]);

  const handleScroll = useCallback((event) => {
    const currentOffset = event.nativeEvent.contentOffset.y;
    scrollOffset.current = currentOffset;
    
    if (currentOffset <= 0) {
      onEndReachedCalledDuringMomentum.current = false;
      isLoadingMoreRef.current = false;
    }

    if (isFocused) {
      Keyboard.dismiss();
      setIsFocused(false);
    }
  }, [isFocused]);

  useEffect(() => {
    return () => {
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (loading) {
      loadingTimeoutRef.current = setTimeout(() => {
        setShowSearchResults(true);
      }, 300);
    } else {
      setShowSearchResults(false);
    }

    return () => {
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current);
      }
    };
  }, [loading]);

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
                <View className="bg-primary-100 px-2 py-1 rounded-lg">
                  <Text className="text-purple-800 font-semibold">ZID {zid}</Text>
                </View>
              </View>

              <Box className="mt-4">
                <Input
                  size="md"
                  className="bg-white border border-gray-200 rounded-xl "
                >
                  <InputField
                    ref={drawerInputRef}
                    placeholder={`Search items in ZID ${zid}...`}
                    value={searchText}
                    onChangeText={handleSearchChange}
                    className="text-sm"
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    autoCorrect={false}
                    spellCheck={false}
                    autoCapitalize="none"
                    returnKeyType="search"
                  />
                  <InputSlot px="$3">
                    <InputIcon as={Search} size={18} className="text-gray-400" />
                  </InputSlot>
                </Input>
              </Box>
            </View>
          </DrawerHeader>

          <View style={{ flex: 1 }} className="bg-gray-100">
            <FlatList
              data={items}
              renderItem={renderItem}
              keyExtractor={(item) => item.item_id}
              ListEmptyComponent={
                <View className="py-5 items-center">
                  <Text className="text-gray-600 text-center">
                    {searchText.length < 1 // Changed from 3 to 1
                      ? "Type at least 1 character to search"
                      : loading
                      ? "Searching..."
                      : "No items found"}
                  </Text>
                </View>
              }
              ListFooterComponent={
                loadingMore ? (
                  <View className="py-5 items-center">
                    <Spinner size="small" color="$primary500" />
                    <Text className="mt-2 text-gray-600">Loading more...</Text>
                  </View>
                ) : null
              }
              onEndReached={handleLoadMore}
              onMomentumScrollBegin={() => {
                onEndReachedCalledDuringMomentum.current = false;
              }}
              onEndReachedThreshold={0.5}
              removeClippedSubviews={false}
              initialNumToRender={10}
              maxToRenderPerBatch={5}
              updateCellsBatchingPeriod={50}
              onScroll={handleScroll}
              scrollEventThrottle={16}
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
