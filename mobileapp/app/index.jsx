
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

        <Box className="justify-center h-80">

    </Box>
    <Center>

    <Grid
      className="gap-5"
      _extra={{
        className: "grid-cols-12",
      }}
    >
      <GridItem
        className="bg-warning-500 p-6 rounded-md"
        _extra={{
          className: "col-span-3",
        }}
      />
      <GridItem
        className="bg-warning-500 p-6 rounded-md"
        _extra={{
          className: "col-span-5",
        }}
      />
      <GridItem
        className="bg-warning-500 p-6 rounded-md"
        _extra={{
          className: "col-span-6",
        }}
      />
      <GridItem
        className="bg-warning-500 p-6 rounded-md"

        _extra={{
          className: "col-span-4",
        }}
      />
      <GridItem
        className="bg-warning-500 p-6 rounded-md"
        _extra={{
          className: "col-span-4",
        }}
      />
    </Grid>
    </Center>
      <Box><Text>Hello world</Text></Box>
      </Center>
    </SafeAreaView>
  );
};

export default index;