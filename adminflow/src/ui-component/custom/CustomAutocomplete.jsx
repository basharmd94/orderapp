import { styled, useTheme } from '@mui/material/styles';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import { getCustomAutocompleteStyles } from './customStyles';

const StyledAutocomplete = styled(Autocomplete)(({ theme }) => ({
  ...getCustomAutocompleteStyles(theme),
  // All other Autocomplete props remain the same
  ...Autocomplete.defaultProps,
}));

// Wrapper component to handle the TextField prop
const CustomAutocomplete = (props) => {
  const theme = useTheme();
  
  return (
    <StyledAutocomplete
      {...props}
      renderInput={(params) => (
        <TextField
          {...params}
          {...props.textFieldProps}
          sx={{
            ...getCustomAutocompleteStyles(theme),
            ...props.textFieldProps?.sx
          }}
        />
      )}
    />
  );
};

export default CustomAutocomplete;