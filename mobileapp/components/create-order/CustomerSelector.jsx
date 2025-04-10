import React, { useState, useCallback, useEffect, useRef, memo } from 'react';
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

// Memoize CustomerCard for better performance
const CustomerCard = memo(({ customer, onSelect }) => (
  <TouchableOpacity
    onPress={onSelect}
    activeOpacity={0.7}
    className="mx-4 my-2"
  >
    <View className="bg-white rounded-2xl border border-gray-200 p-4">
      <View className="flex-row items-center">
        <View className="bg-warning-50 p-3 rounded-xl mr-3">
          <Building size={20} className="text-warning-500" />
        </View>
        <View className="flex-1">
          <Text className="text-lg font-semibold text-gray-900" numberOfLines={1} ellipsizeMode="tail">
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
          <Text className="ml-2 text-sm text-gray-600" numberOfLines={1} ellipsizeMode="tail">
            {customer.xtaxnum || 'No phone'}
          </Text>
        </View>
        <View className="flex-row items-center flex-1">
          <MapPin size={16} color="#666666" />
          <Text className="ml-2 text-sm text-gray-600" numberOfLines={1} ellipsizeMode="tail">
            {customer.xcity || 'No city'}
          </Text>
        </View>
      </View>

      {customer.xadd1 && (
        <View className="bg-gray-100 p-2 rounded-lg mt-2">
          <Text className="text-sm text-gray-600" numberOfLines={2} ellipsizeMode="tail">{customer.xadd1}</Text>
        </View>
      )}
    </View>
  </TouchableOpacity>
));

// Use React.memo for the whole component for better performance
export default function CustomerSelector({
  zid,
  customerName,
  disabled,
  showCustomerSheet,
  setShowCustomerSheet,
  onCustomerSelect,
  customers,
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
        // Clear customers when search is empty
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
    if (showCustomerSheet) {
      setLocalSearchText(searchText || '');
      
      // Only trigger search on initial open if searchText exists
      if (searchText?.length >= 1 && !initialSearchDoneRef.current) {
        initialSearchDoneRef.current = true;
        setTimeout(() => {
          onSearch(searchText);
        }, 0);
      }
    } else {
      // Reset flag when drawer closes
      initialSearchDoneRef.current = false;
    }
  }, [showCustomerSheet, searchText, onSearch]);

  const handleClearSearch = useCallback(() => {
    setLocalSearchText('');
    setSearchText('');
    onSearch('');
  }, [setSearchText, onSearch]);

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
              data={customers}
              renderItem={renderItem}
              keyExtractor={getItemKey}
              ListEmptyComponent={
                <View className="py-5 items-center">
                  <Text className="text-gray-600 text-center">
                    {localSearchText.length < 1
                      ? "Type at least 1 character to search"
                      : loading
                      ? "Searching..."
                      : "No customers found"}
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