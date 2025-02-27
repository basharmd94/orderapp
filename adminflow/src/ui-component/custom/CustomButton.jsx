import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import { getCustomButtonStyles } from './customStyles';

const CustomButton = styled(Button)(({ theme }) => ({
  ...getCustomButtonStyles(theme),
  // All other Button props remain the same
  ...Button.defaultProps,
}));

export default CustomButton;