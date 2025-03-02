import { SafeAreaView } from "react-native-safe-area-context";
import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { Heading } from "@/components/ui/heading";
import { ScrollView, View, TouchableOpacity } from "react-native";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Button, ButtonText, ButtonIcon, ButtonSpinner } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { Avatar } from "@/components/ui/avatar";
import { AvatarFallbackText } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Divider } from "@/components/ui/divider";
import { LogOut, Mail, Phone, Building, Terminal, Shield, Database, Package } from 'lucide-react-native';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { useState } from 'react';
import syncCustomers from '@/utils/syncCustomer';
import syncItems from '@/utils/syncItems';
import colors from "tailwindcss/colors";
import { Alert, AlertText, AlertIcon } from "@/components/ui/alert";
import { InfoIcon } from "@/components/ui/icon";

const ProfileItem = ({ icon: Icon, label, value }) => (
  <HStack space="md" className="items-center py-3">
    <Box className="bg-orange-400 p-2 rounded-lg">
      <Icon size={20} color="#fff" />
    </Box>
    <VStack>
      <Text className="text-gray-500 text-sm">{label}</Text>
      <Text className="text-gray-900 font-medium">{value}</Text>
    </VStack>
  </HStack>
);

const ActionButton = ({ icon: Icon, label, onPress, isLoading, color }) => (
  <TouchableOpacity 
    onPress={onPress} 
    disabled={isLoading}
    className="items-center justify-center"
  >
    <Box 
      className={`w-16 h-16 rounded-full items-center justify-center ${color}`}
    >
      {isLoading ? (
        <ButtonSpinner color={colors.white} />
      ) : (
        <Icon size={25} color="#fff" />
      )}
    </Box>
    <Text className="text-xs text-gray-700 mt-2 font-medium text-center">
      {isLoading ? 'Syncing...' : label}
    </Text>
  </TouchableOpacity>
);

export default function Profile() {
  const { user, logout } = useAuth();
  const [isSyncingCustomers, setIsSyncingCustomers] = useState(false);
  const [isSyncingItems, setIsSyncingItems] = useState(false);
  const [syncAlert, setSyncAlert] = useState({ show: false, message: '' });

  const getInitials = (name) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase();
  };

  const handleSyncCustomers = async () => {
    if (!user?.user_id) {
      console.error('No employee ID available for sync');
      return;
    }
    setIsSyncingCustomers(true);
    setSyncAlert({ show: false, message: '' });
    try {
      const result = await syncCustomers(user.user_id);
      if (result.success) {
        let message = result.message;
        if (!message) {
          if (result.totalCustomers === -1) {
            message = 'Customer sync completed successfully';
          } else {
            message = `Customer Sync Completed: ${result.updatedCustomers} customers updated out of ${result.totalCustomers} total customers`;
          }
        }
        setSyncAlert({ show: true, message });
      }
    } catch (error) {
      console.error('Customer sync failed:', error);
      setSyncAlert({ show: true, message: 'Customer Sync Failed!' });
    } finally {
      setIsSyncingCustomers(false);
    }
  };

  const handleSyncItems = async () => {
    setIsSyncingItems(true);
    setSyncAlert({ show: false, message: '' });
    try {
      const result = await syncItems();
      if (result.success) {
        let message = result.message;
        if (!message) {
          if (result.totalItems === -1) {
            message = 'Item sync completed successfully';
          } else {
            message = `Items Sync Completed: ${result.updatedItems} items updated out of ${result.totalItems} total items`;
          }
        }
        setSyncAlert({ show: true, message });
      }
    } catch (error) {
      console.error('Items sync failed:', error);
      setSyncAlert({ show: true, message: 'Items Sync Failed!' });
    } finally {
      setIsSyncingItems(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-primary-">
      <ScrollView>
        <Box className="p-4">
          <Animated.View 
            entering={FadeInDown.duration(500).springify()}
            className="items-center mb-4"
          >
            <Avatar size="2xl" className="bg-orange-400 mb-4">
              <AvatarFallbackText>
                {getInitials(user?.username || 'User')}
              </AvatarFallbackText>
            </Avatar>
            <Heading size="xl" className="text-gray-900">
              {user?.username || 'User'}
            </Heading>
            <Text className="text-gray-500 mt-1 mb-4">
              Employee ID: {user?.user_id || 'N/A'}
            </Text>
            
            {/* New horizontal grid of action buttons */}
            <Animated.View 
              entering={FadeInDown.delay(50).duration(500).springify()}
              className="w-full"
            >
              <HStack space="lg" className="justify-center mb-4">
                <ActionButton 
                  icon={Package} 
                  label="Sync Items" 
                  onPress={handleSyncItems}
                  isLoading={isSyncingItems}
                  color="bg-emerald-500"
                />

                <ActionButton 
                  icon={Database} 
                  label="Sync Customers" 
                  onPress={handleSyncCustomers}
                  isLoading={isSyncingCustomers}
                  color="bg-orange-400"
                />
                <ActionButton 
                  icon={LogOut} 
                  label="Logout" 
                  onPress={logout}
                  
                  color="bg-gray-800"
                />
              </HStack>
            </Animated.View>
          </Animated.View>

          <Animated.View 
            entering={FadeInDown.delay(100).duration(500).springify()}
          >
            <Card className="bg-white rounded-2xl p-4 mb-4">
              <VStack space="xs">
                <Text className="text-gray-900 font-medium mb-2">Profile Information</Text>
                <ProfileItem 
                  icon={Mail} 
                  label="Email Address" 
                  value={user?.email || 'Not provided'} 
                />
                <Divider />
                <ProfileItem 
                  icon={Phone} 
                  label="Mobile Number" 
                  value={user?.mobile || 'Not provided'} 
                />
                <Divider />
                <ProfileItem 
                  icon={Building} 
                  label="Business ID" 
                  value={user?.businessId || 'Not assigned'} 
                />
                <Divider />
                <ProfileItem 
                  icon={Terminal} 
                  label="Terminal" 
                  value={user?.terminal || 'Not assigned'} 
                />
                <Divider />
                <ProfileItem 
                  icon={Shield} 
                  label="Role" 
                  value={user?.is_admin === 'admin' ? 'Administrator' : 'User'} 
                />
              </VStack>
            </Card>

            {/* Sync Alert */}
            {syncAlert.show && (
              <Animated.View entering={FadeInDown.duration(300)}>
                <Alert action="info" variant="solid" className="mb-4">
                  <AlertIcon as={InfoIcon} />
                  <AlertText>{syncAlert.message}</AlertText>
                </Alert>
              </Animated.View>
            )}

            {/* Original buttons removed from here */}
          </Animated.View>
        </Box>
      </ScrollView>
    </SafeAreaView>
  );
}