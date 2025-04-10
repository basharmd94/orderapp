import { StatusBar } from "expo-status-bar";
import { Redirect, router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { ButtonText } from "@/components/ui/button";
import { Box } from "@/components/ui/box";
import { Center } from "@/components/ui/center";
import { Heading } from "@/components/ui/heading";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { Spinner } from "@/components/ui/spinner";

const index = () => {
  const { loading, user } = useAuth();

  if (!loading && user) return <Redirect href="/(tabs)/home" />;

  return (
    <SafeAreaView className="bg-primary h-full">
      {loading && (
        <Box position="absolute" top={0} left={0} right={0} zIndex={1000}>
          <Center py="$4">
            <Spinner size="large" color="$primary500" />
          </Center>
        </Box>
      )}
      
      <Center flex={1}>
        <VStack space="md" p="$4" alignItems="center">
          <Box mb="$8">
            <Heading size="2xl" color="$white" textAlign="center">
              Welcome to HMBR OrderApp
            </Heading>
            <Heading size="lg" color="$secondary200" textAlign="center" mt="$2">
              HMBR Order Management Solution
            </Heading>
          </Box>

          <Text
            size="sm"
            color="$gray100"
            textAlign="center"
            mb="$8"
          >
            Streamline your orders and boost your business efficiency with our comprehensive solution
          </Text>

          <Button
            size="lg"
            variant="solid"
            action="primary"
            isDisabled={loading}
            width="$full"
            onPress={() => router.push("/sign-in")}
          >
            <ButtonText>Continue with Email</ButtonText>
          </Button>
        </VStack>
      </Center>

      <StatusBar style="light" backgroundColor="#161622" />
    </SafeAreaView>
  );
};

export default index;