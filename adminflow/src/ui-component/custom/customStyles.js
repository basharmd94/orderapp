// Shared styles for custom components
export const getCustomInputStyles = (theme) => ({
  '& label.Mui-focused': {
    color: theme.palette.secondary.main,
  },
  '& .MuiOutlinedInput-root': {
    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
      borderColor: theme.palette.secondary.main,
    },
  },
});

export const getCustomButtonStyles = (theme) => ({
  backgroundColor: theme.palette.secondary.dark,
  color: '#fff',
  '&:hover': {
    backgroundColor: theme.palette.secondary.main,
  },
  '&.Mui-disabled': {
    backgroundColor: theme.palette.secondary.light,
  },
});

export const getCustomAutocompleteStyles = (theme) => ({
  '& .MuiOutlinedInput-root': {
    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
      borderColor: theme.palette.secondary.main,
    },
  },
  '& .MuiInputLabel-root.Mui-focused': {
    color: theme.palette.secondary.main,
  },
});