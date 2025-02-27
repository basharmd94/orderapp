import React, { useState } from 'react';
import { Stack, Typography } from '@mui/material';
import { CustomInput, CustomButton, CustomAutocomplete } from './index';

const CustomComponentsDemo = () => {
  const [value, setValue] = useState('');
  const [autoValue, setAutoValue] = useState(null);

  const options = [
    { label: 'Option 1', value: 1 },
    { label: 'Option 2', value: 2 },
    { label: 'Option 3', value: 3 },
  ];

  return (
    <Stack spacing={3} sx={{ maxWidth: 400, m: 2 }}>
      <Typography variant="h6">Custom Components Demo</Typography>
      
      <CustomInput
        label="Custom Input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        fullWidth
      />

      <CustomAutocomplete
        options={options}
        value={autoValue}
        onChange={(_, newValue) => setAutoValue(newValue)}
        getOptionLabel={(option) => option.label}
        renderInput={(params) => (
          <CustomInput
            {...params}
            label="Custom Autocomplete"
          />
        )}
      />

      <CustomButton variant="contained">
        Custom Button
      </CustomButton>
    </Stack>
  );
};

export default CustomComponentsDemo;