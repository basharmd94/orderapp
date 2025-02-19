import { Center } from '@/components/ui/center';
import { Text } from '@/components/ui/text';
import { Link, Stack } from 'expo-router';



export default function NotFoundScreen() {
  return (
    <>
      <Stack.Screen options={{ title: 'Oops!' }} />
      <Center>
        <Text type="title">This screen doesn't exist.</Text>
        <Link href="/" style={styles.link}>
          <Text type="link">Go to home screen!</Text>
        </Link>
      </Center>
    </>
  );
}
