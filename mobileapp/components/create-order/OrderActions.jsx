import { Box } from "@/components/ui/box";
import { Button, ButtonIcon, ButtonText } from "@/components/ui/button";
import { ShoppingCart } from "lucide-react-native";
import { EditIcon } from "@/components/ui/icon"

export default function OrderActions({
  onAddToCart,
  addToCartDisabled,
}) {
  return (
    <Box>
      <Button
        onPress={onAddToCart}
        disabled={addToCartDisabled}
        className="w-full"
      >
        <ButtonIcon as={EditIcon} />
        <ButtonText>Add to Cart</ButtonText>
      </Button>
    </Box>
  );
}