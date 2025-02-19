import { Alert, AlertText, AlertIcon } from "@/components/ui/alert";
import { InfoIcon } from "@/components/ui/icon";
import {SafeAreaView, SafeAreaview} from "react-native-safe-area-context";	
import { Center } from "../../components/ui/center";



export default function Home() {
  return (
    
    <SafeAreaView style = {{flex: 1, width: '100%', height: '100%', justifyContent: 'center', alignItems: 'center'}}>
        <Center>

      <Alert action="warning" variant="solid" >
          <AlertIcon as={InfoIcon} />
          <AlertText>
            Description of alert!
          </AlertText>
        </Alert>
        </Center>
    </SafeAreaView>
    
  );
}