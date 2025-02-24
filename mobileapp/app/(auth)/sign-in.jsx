import React from 'react';
import { Link } from 'expo-router';
import { useState } from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { 
  FadeInDown, 
  FadeInUp
} from 'react-native-reanimated';
import { Box } from '@/components/ui/box';
import { Button } from '@/components/ui/button';
import { ButtonText, ButtonIcon, ButtonSpinner } from '@/components/ui/button';
import { Center } from '@/components/ui/center';
import { FormControl } from '@/components/ui/form-control';
import { FormControlLabel, FormControlLabelText } from '@/components/ui/form-control';
import { Heading } from '@/components/ui/heading';
import { VStack } from '@/components/ui/vstack';
import { Text } from '@/components/ui/text';
import { Input } from '@/components/ui/input';
import { InputField, InputSlot, InputIcon } from '@/components/ui/input';
import { EyeIcon, EyeOffIcon, LogInIcon } from 'lucide-react-native';
import { Alert, AlertText, AlertIcon } from '@/components/ui/alert';
import { InfoIcon } from '@/components/ui/icon';
import { useAuth } from '@/context/AuthContext';

const SignIn = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!username || !password) {
      setError('Please fill in all fields');
      return;
    }
    try {
      setIsLoading(true);
      setError('');
      await login(username, password);
    } catch (err) {
      // Handle validation errors
      if (err.response?.data?.detail && Array.isArray(err.response.data.detail)) {
        // Join multiple validation errors into a single message
        setError(err.response.data.detail.map(e => e.msg).join(', '));
      } else {
        setError(err.response?.data?.detail || 'Login failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = username.length > 0 && password.length > 0;

  return (
    <SafeAreaView className="flex-1 bg-gray-100">
      <Center className="flex-1 px-4">
        <Box className="w-full max-w-[400px]">
          <VStack space="md">
            <Animated.View entering={FadeInDown.duration(1000).springify()}>
              <Center className="mb-6">
                <Heading size="2xl" className="text-primary">
                  Welcome Back
                </Heading>
                <Text size="sm" className="text-gray-400">
                  Please sign in to your account
                </Text>
              </Center>
            </Animated.View>

            {error && (
              <Animated.View entering={FadeInDown.duration(1000).springify()}>
                <Alert action="error" variant="solid" mb="$3">
                  <AlertIcon as={InfoIcon} />
                  <AlertText>{error}</AlertText>
                </Alert>
              </Animated.View>
            )}

            <Animated.View entering={FadeInUp.delay(400).duration(1000).springify()}>
              <FormControl className="mb-4">
                <FormControlLabel>
                  <FormControlLabelText className="text-gray-400">Username</FormControlLabelText>
                </FormControlLabel>
                <Input
                  variant="outline"
                  size="xl"
                >
                  <InputField
                    placeholder="Enter your username"
                    value={username}
                    onChangeText={setUsername}
                    className="text-primary-400"
                    placeholderTextColor="gray-100"
                  />
                </Input>
              </FormControl>
            </Animated.View>

            <Animated.View entering={FadeInUp.delay(600).duration(1000).springify()}>
              <FormControl className="mb-6">
                <FormControlLabel>
                  <FormControlLabelText className="text-gray-400">Password</FormControlLabelText>
                </FormControlLabel>
                <Input size="xl">
                  <InputField
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={password}
                    onChangeText={setPassword}
                    className="text-primary-500"
                    placeholderTextColor={"#0000"}
                  />
                  <InputSlot 
                    onPress={() => setShowPassword(!showPassword)}
                    className="pr-3"
                  >
                    <InputIcon 
                      as={showPassword ? EyeOffIcon : EyeIcon} 
                      className="text-gray-500"
                    />
                  </InputSlot>
                </Input>
              </FormControl>
            </Animated.View>

            <Animated.View entering={FadeInUp.delay(800).duration(1000).springify()}>
              <Button
                size="lg"
                variant="solid"
                action="primary"
                isDisabled={!isFormValid || isLoading}
                onPress={handleLogin}
                className="mb-6 bg-primary-800 disabled:bg-gray-700"
              >
                {isLoading ? (
                  <ButtonSpinner className="mr-2" />
                ) : (
                  <ButtonIcon as={LogInIcon} className="mr-2" />
                )}
                <ButtonText>
                  {isLoading ? "Signing In..." : "Sign In"}
                </ButtonText>
              </Button>

              <Center className="mt-6">
                <Text className="text-gray-400">
                  Don't have an account?{' '}
                  <Link href="../(auth)/sign-up" asChild>
                    <Text className="text-info-600 font-bold">
                      Sign Up
                    </Text>
                  </Link>
                </Text>
              </Center>

              <Center className="mt-4">
                <Link href="../(auth)/forgot-password" asChild>
                  <Text className="text-gray-400 underline">
                    Forgot Password?
                  </Text>
                </Link>
              </Center>
            </Animated.View>
          </VStack>
        </Box>
      </Center>
    </SafeAreaView>
  );
};

export default SignIn;