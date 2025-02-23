import { Box } from "@/components/ui/box";
import { Text } from "@/components/ui/text";
import { Input, InputField, InputSlot  } from "@/components/ui/input";
import { Plus } from "lucide-react-native";


export default function QuantityInput({
  quantity,
  setQuantity,
  disabled
}) {
  return (
    <Box>
      <Text className="text-primary-100 text-xs pb-2">Quantity</Text>
      <Input size="md" variant="rounded" className = 'border border'>
        <InputField
          placeholder="Enter quantity"
          value={quantity}
          onChangeText={setQuantity}
          keyboardType="numeric"
          disabled={disabled}    
          className = "text-xs"    
          
          
        />

            <InputSlot className="flex justify-center items-center">
              <Plus className="w-5 h-5 text-gray-500 mr-4" />
            </InputSlot>
            

      </Input>
    </Box>
  );
} 