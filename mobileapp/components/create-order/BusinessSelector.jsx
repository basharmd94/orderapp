import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { Button, ButtonIcon, ButtonText } from "@/components/ui/button";
import { ChevronDown, Building2 } from "lucide-react-native";
import {
  Drawer,
  DrawerBackdrop,
  DrawerContent,
  DrawerHeader,
  DrawerBody,
} from "@/components/ui/drawer";
import { View } from "react-native";
import { Heading } from "@/components/ui/heading";
import { VStack } from "@/components/ui/vstack";

const BusinessCard = ({ name, id, onSelect }) => (
  <Button
    variant="outline"
    onPress={onSelect}
    className="mx-4 my-2 p-0 h-auto bg-white border border-gray-200 rounded-2xl"
  >
    <View className="p-4 w-full">
      <View className="flex-row items-center">
        <View className="bg-warning-50 p-3 rounded-xl mr-3">
          <Building2 size={20} className="text-warning-500" />
        </View>
        <View className="flex-1">
          <Text className="text-lg font-semibold text-gray-900">
            {name}
          </Text>
          <Text className="text-sm text-gray-600 mt-1">
            ID: {id}
          </Text>
        </View>
      </View>
    </View>
  </Button>
);

export default function BusinessSelector({
  zid,
  onZidSelect,
  disabled,
  showZidSheet,
  setShowZidSheet,
}) {
  const zids = {
    'GI Corp': '100000',
    'HMBR': '100001',
    'Zepto': '100005'
  };

  return (
    <Box>
      <Text className="text-primary-100 text-xs mb-2">Business zid</Text>
      
      <Button
        variant="outline"
        onPress={() => setShowZidSheet(true)}
        disabled={disabled}
        className="border border-primary-50 rounded-2xl flex-row items-center justify-between"
      >
        <ButtonText className="text-primary-200 text-xs">{zid || "Select ZID"}</ButtonText>
        <ButtonIcon as={ChevronDown} className="text-primary-50" />
      </Button>

      <Drawer
        isOpen={showZidSheet}
        onClose={() => setShowZidSheet(false)}
        size="full"
        anchor="bottom"
      >
        <DrawerBackdrop />
        <DrawerContent className="h-full">
          <DrawerHeader className="bg-white border-b border-gray-100">
            <View className="p-4">
              <Text className="text-xs text-gray-600 uppercase mb-1">Select Business</Text>
              <View className="flex-row justify-between items-center">
                <Heading size="lg">Business</Heading>
                <View className="bg-warning-50 px-2 py-1 rounded-lg">
                  <Text className="text-warning-700 font-semibold">Admin</Text>
                </View>
              </View>
            </View>
          </DrawerHeader>
          <View className="flex-1 bg-gray-100 p-2">
            <VStack space="xs">
              {Object.entries(zids).map(([name, id]) => (
                <BusinessCard
                  key={id}
                  name={name}
                  id={id}
                  onSelect={() => {
                    onZidSelect(id);
                    setShowZidSheet(false);
                  }}
                />
              ))}
            </VStack>
          </View>
        </DrawerContent>
      </Drawer>
    </Box>
  );
}