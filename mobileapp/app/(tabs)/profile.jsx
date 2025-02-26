import { SafeAreaView } from "react-native-safe-area-context";
import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { Heading } from "@/components/ui/heading";
import { ScrollView } from "react-native";
import { VStack } from "@/components/ui/vstack";
import { HStack } from "@/components/ui/hstack";
import { Button, ButtonText, ButtonIcon, ButtonSpinner } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { Avatar } from "@/components/ui/avatar";
import { AvatarFallbackText } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Divider } from "@/components/ui/divider";
import { LogOut, Mail, Phone, Building, Terminal, Shield, Database } from 'lucide-react-native';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { useState } from 'react';
import syncCustomers from '@/utils/syncCustomer';
import colors from "tailwindcss/colors";
import { Alert, AlertText, AlertIcon } from "@/components/ui/alert"; // Added Alert imports
import { InfoIcon } from "@/components/ui/icon"; // Added InfoIcon

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

export default function Profile() {
  const { user, logout } = useAuth();
  const [isSyncing, setIsSyncing] = useState(false);
  const [showSyncAlert, setShowSyncAlert] = useState(false); // State for alert

  const getInitials = (name) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase();
  };

  const handleSync = async () => {
    if (!user?.user_id) {
      console.error('No employee ID available for sync');
      return;
    }
    setIsSyncing(true);
    setShowSyncAlert(false); // Reset alert
    try {
      const success = await syncCustomers(user.user_id);
      if (success) {
        setShowSyncAlert(true); // Show alert on success
      }
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-primary-">
      <ScrollView>
        <Box className="p-4">
          <Animated.View 
            entering={FadeInDown.duration(500).springify()}
            className="items-center mb-6"
          >
            <Avatar size="2xl" className="bg-orange-400 mb-4">
              <AvatarFallbackText>
                {getInitials(user?.employee_name || user?.username || 'User')}
              </AvatarFallbackText>
            </Avatar>
            <Heading size="xl" className="text-gray-900">
              {user?.employee_name || user?.username || 'User'}
            </Heading>
            <Text className="text-gray-500 mt-1">
              Employee ID: {user?.user_id || 'N/A'}
            </Text>
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
            {showSyncAlert && (
              <Animated.View entering={FadeInDown.duration(300)}>
                <Alert action="info" variant="solid" className="mb-4">
                  <AlertIcon as={InfoIcon} />
                  <AlertText>Sync Completed Successfully!</AlertText>
                </Alert>
              </Animated.View>
            )}

            {/* Sync Customers Button */}
            <Button
              size="lg"
              variant="solid"
              action="primary"
              onPress={handleSync}
              className="mt-4 bg-blue-500"
              isDisabled={isSyncing}
            >
              {isSyncing ? (
                <>
                  <ButtonSpinner color={colors.gray[400]} />
                  <ButtonText className="font-medium text-sm ml-2 text-white">
                    Syncing...
                  </ButtonText>
                </>
              ) : (
                <>
                  <ButtonIcon as={Database} className="mr-2 text-white" />
                  <ButtonText className="text-white">Sync Customers</ButtonText>
                </>
              )}
            </Button>

            {/* Logout Button */}
            <Button
              size="lg"
              variant="outline"
              action="error"
              onPress={logout}
              className="mt-4 bg-orange-400 border-0"
            >
              <ButtonIcon as={LogOut} className="mr-2 text-error-600 text-white" />
              <ButtonText>Logout</ButtonText>
            </Button>
          </Animated.View>
        </Box>
      </ScrollView>
    </SafeAreaView>
  );
}