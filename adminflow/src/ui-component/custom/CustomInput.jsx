import { styled } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import { getCustomInputStyles } from './customStyles';

const CustomInput = styled(TextField)(({ theme }) => ({
  ...getCustomInputStyles(theme),
  // Preserving all other default props and styles
  ...TextField.defaultProps,
}));

export default CustomInput;