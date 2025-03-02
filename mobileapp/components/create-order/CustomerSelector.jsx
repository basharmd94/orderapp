import React, { useState, useCallback, useEffect, useRef } from 'react';
import { View, FlatList, TouchableOpacity, Keyboard } from 'react-native';
import { Input, InputField, InputIcon, InputSlot } from '@/components/ui/input';
import { ChevronDown, Search, X, Phone, MapPin, Building } from 'lucide-react-native';
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

const CustomerCard = ({ customer, onSelect }) => (
  <TouchableOpacity
    onPress={onSelect}
    activeOpacity={0.7}
    className="mx-4 my-2"
  >
    <View className="bg-white rounded-2xl border border-gray-200  p-4">
      <View className="flex-row items-center">
        <View className="bg-warning-50 p-3 rounded-xl mr-3">
          <Building size={20} className = "text-warning-500" />
        </View>
        <View className="flex-1">
          
          <Text className="text-lg font-semibold text-gray-900">
            {customer.xorg}
          </Text>
          <Text className="text-sm text-gray-600 mt-1">
            ID: {customer.xcus}
          </Text>
        </View>
      </View>

      <View className="h-px bg-gray-200 my-3" />

      <View className="flex-row justify-between mt-1">
        <View className="flex-row items-center flex-1">
          <Phone size={16} color="#666666" />
          <Text className="ml-2 text-sm text-gray-600">
            {customer.xtaxnum || 'No phone'}
          </Text>
        </View>
        <View className="flex-row items-center flex-1">
          <MapPin size={16} color="#666666" />
          <Text className="ml-2 text-sm text-gray-600 truncate">
            {customer.xcity || 'No city'}
          </Text>
        </View>
      </View>

      {customer.xadd1 && (
        <View className="bg-gray-100 p-2 rounded-lg mt-2">
          <Text className="text-sm text-gray-600">{customer.xadd1}</Text>
        </View>
      )}
    </View>
  </TouchableOpacity>
);

export default function CustomerSelector({
  zid,
  customerName,
  disabled,
  showCustomerSheet,
  setShowCustomerSheet,
  onCustomerSelect,
  customers,
  loading,
  loadingMore,
  searchText,
  setSearchText,
  onLoadMore,
  hasMoreData,
  onSearch, // Added param for search function
}) {
  const inputRef = useRef(null);
  const drawerInputRef = useRef(null);
  const [isFocused, setIsFocused] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [autocompleteResults, setAutocompleteResults] = useState([]);
  const loadingTimeoutRef = useRef(null);
  const isTypingRef = useRef(false);
  const scrollOffset = useRef(0);
  const onEndReachedCalledDuringMomentum = useRef(false);
  const isLoadingMoreRef = useRef(false);

  // Create debounced search function
  const debouncedSearch = useRef(
    debounce((text) => {
      if (text.length >= 1) {
        onSearch(text);
        setShowAutocomplete(true);
      } else {
        setShowAutocomplete(false);
        setAutocompleteResults([]);
      }
    }, 300)
  ).current;

  // Update autocomplete results when customers change
  useEffect(() => {
    if (searchText.length >= 1 && !loading) {
      setAutocompleteResults(customers.slice(0, 5)); // Show top 5 matches as autocomplete
    }
  }, [customers, loading, searchText]);

  const handleSearchChange = useCallback((text) => {
    setSearchText(text);
    isTypingRef.current = true;
    debouncedSearch(text);
  }, [setSearchText, debouncedSearch]);

  const handleAutocompleteSelect = useCallback((item) => {
    setSearchText(item.xorg);
    setShowAutocomplete(false);
    onSearch(item.xorg);
  }, [setSearchText, onSearch]);

  const handleLoadMore = useCallback(() => {
    if (onEndReachedCalledDuringMomentum.current) return;
    
    if (!loading && 
        !loadingMore && 
        hasMoreData && 
        searchText.length >= 1 && 
        !isLoadingMoreRef.current && 
        scrollOffset.current > 0) {
      isLoadingMoreRef.current = true;
      onLoadMore();
      onEndReachedCalledDuringMomentum.current = true;
    }
  }, [loading, loadingMore, hasMoreData, searchText, onLoadMore]);

  const handleScroll = useCallback((event) => {
    const currentOffset = event.nativeEvent.contentOffset.y;
    scrollOffset.current = currentOffset;
    
    if (currentOffset <= 0) {
      onEndReachedCalledDuringMomentum.current = false;
      isLoadingMoreRef.current = false;
    }
  }, []);

  useEffect(() => {
    return () => {
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current);
      }
      // Clean up debounce function
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

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
    <CustomerCard
      customer={item}
      onSelect={() => {
        onCustomerSelect(item);
        setShowCustomerSheet(false);
        Keyboard.dismiss();
      }}
    />
  ), [onCustomerSelect, setShowCustomerSheet]);

  const renderAutocompleteItem = useCallback(({ item }) => (
    <TouchableOpacity
      onPress={() => handleAutocompleteSelect(item)}
      className="px-4 py-2 border-b border-gray-100"
    >
      <View className="flex-row items-center">
        <Building size={16} className="text-gray-400 mr-2" />
        <Text className="text-gray-800 font-medium">{item.xorg}</Text>
      </View>
      <Text className="text-xs text-gray-500 ml-6">
        {item.xcity ? `${item.xcity}${item.xtaxnum ? ` • ${item.xtaxnum}` : ''}` : 
          item.xtaxnum ? item.xtaxnum : 'ID: ' + item.xcus}
      </Text>
    </TouchableOpacity>
  ), [handleAutocompleteSelect]);

  const getItemKey = useCallback((item) => 
    `customer-${item.xcus}-${item.zid}`, 
  []);

  return (
    <VStack space="md">
      <Button
        variant="outline"
        className="border border-primary-50 rounded-2xl flex-row items-center justify-between"
        onPress={() => setShowCustomerSheet(true)}
        disabled={disabled}
      >
        <ButtonText className="text-primary-200 text-xs">
          {customerName || "Select Customer"}
        </ButtonText>
        <ButtonIcon as={ChevronDown} className="text-primary-50" /> 
      </Button>

      <Drawer
        isOpen={showCustomerSheet}
        onClose={() => {
          setShowCustomerSheet(false);
          setShowAutocomplete(false);
          Keyboard.dismiss();
        }}
        size="full"
        anchor="bottom"
      >
        <DrawerBackdrop />
        <DrawerContent className="h-full w-full">
          <DrawerHeader className="bg-white border-b border-gray-100 w-full">
            <View className="p-4">
              <Text className="text-xs text-gray-600 uppercase mb-1">Select Customer from</Text>
              <View className="flex-row justify-between items-center">
                <Heading size="lg">Business</Heading>
                <View className="bg-warning-50 px-2 py-1 rounded-lg">
                  <Text className="text-warning-700 font-semibold">ZID {zid}</Text>
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
                      placeholder={`Search customers in ZID ${zid}...`}
                      value={searchText}
                      onChangeText={handleSearchChange}
                      className="text-sm"
                      onFocus={() => {
                        setIsFocused(true);
                        if (searchText.length >= 1 && autocompleteResults.length > 0) {
                          setShowAutocomplete(true);
                        }
                      }}
                      onBlur={() => {
                        setIsFocused(false);
                        // Delay hiding autocomplete to allow for selection
                        setTimeout(() => setShowAutocomplete(false), 150);
                      }}
                      autoCorrect={false}
                      spellCheck={false}
                      autoCapitalize="none"
                      returnKeyType="search"
                    />
                    <InputSlot px="$3">
                      {searchText ? (
                        <TouchableOpacity 
                          onPress={() => {
                            setSearchText('');
                            setShowAutocomplete(false);
                          }}
                          hitSlop={{ top: 10, right: 10, bottom: 10, left: 10 }}
                        >
                          <InputIcon as={X} size={18} className="text-gray-400" />
                        </TouchableOpacity>
                      ) : (
                        <InputIcon as={Search} size={18} className="text-gray-400" />
                      )}
                    </InputSlot>
                  </Input>
                  
                  {/* Autocomplete dropdown */}
                  {showAutocomplete && autocompleteResults.length > 0 && (
                    <View className="absolute top-12 left-0 right-0 bg-white rounded-lg shadow-lg z-10 max-h-64 overflow-hidden">
                      <FlatList
                        data={autocompleteResults}
                        renderItem={renderAutocompleteItem}
                        keyExtractor={getItemKey}
                        keyboardShouldPersistTaps="handled"
                      />
                    </View>
                  )}
                </View>
              </Box>
            </View>
          </DrawerHeader>

          <View style={{ flex: 1 }} className="bg-gray-100">
            <FlatList
              data={customers}
              renderItem={renderItem}
              keyExtractor={getItemKey}
              ListEmptyComponent={
                <View className="py-5 items-center">
                  <Text className="text-gray-600 text-center">
                    {searchText.length < 1
                      ? "Type at least 1 character to search"
                      : loading
                      ? "Searching..."
                      : "No customers found"}
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
                flexGrow: customers.length === 0 ? 1 : undefined,
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