import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { motion } from 'framer-motion';

const LoadingSpinner = ({ message = 'Loading...' }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
  >
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="100vh"
      sx={{
        background: '#f5f5f5',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          background: 'linear-gradient(45deg, #42a5f515, #ba68c815)',
          borderRadius: '0 0 0 100%',
          width: '40%',
          height: '40%',
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          bottom: 0,
          left: 0,
          background: 'linear-gradient(45deg, #42a5f515, #ba68c815)',
          borderRadius: '0 100% 0 0',
          width: '40%',
          height: '40%',
        }
      }}
    >
      <CircularProgress
        size={60}
        thickness={4}
        sx={{
          color: 'primary.main',
          mb: 2,
        }}
      />
      <Typography
        variant="h6"
        sx={{
          color: 'text.primary',
          fontWeight: 500
        }}
      >
        {message}
      </Typography>
    </Box>
  </motion.div>
);

export default LoadingSpinner;