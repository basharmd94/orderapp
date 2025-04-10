import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'

const AuthLayout = () => {
  return (

    <>
      <Stack>

        <Stack.Screen
          options={{ 
            headerShown: false,
            backgroundColor : 'transparent', 
            headerTitle: '',

          }}
          name='sign-up'
        />
        <Stack.Screen 
          options={{ 
            headerShown: false, 
            gestureEnabled: true,
            headerTitle: '',
            backgroundColor : 'transparent',
          
          }}
          name='sign-in'
        />
      </Stack>

      <StatusBar backgroundColor= "#FF914D" style='light'/>
    </>

  )
}

export default AuthLayout