
import { SafeAreaView } from 'react-native-safe-area-context';
import { Box } from '@/components/ui/box';
import { Button } from '@/components/ui/button';
import { Center } from '@/components/ui/center';
import { Text } from '@/components/ui/text';

import {Link} from 'expo-router'
import { VStack } from '@/components/ui/vstack';
import { Grid, GridItem } from '@/components/ui/grid';


const index = () => {

  return (
    <SafeAreaView className="flex-1 bg-gray-100">
    <Center>
      <VStack >
        <Text className="text-2xl text-primary">Welcome to Gluestack</Text>
        <Text className="text-gray-400">This is a simple starter template for Gluestack</Text>
        <Center className="mt-4 flex justify-center align-center w-full max-w-[400px] ">
          <Link href="sign-in">
            <Text>Get Started</Text>
          </Link>
        </Center>
      </VStack>
    </Center>


    </SafeAreaView>
  )
};

export default index;