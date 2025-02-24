import React from 'react';
import { Box, Typography, Card, Grid } from '@mui/material';
import { motion } from 'framer-motion';

const CustomersPage = () => {
  return (
    <Box sx={{ p: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" sx={{ mb: 4, fontWeight: 600 }}>
          Customer Management
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Coming Soon
              </Typography>
              <Typography color="text.secondary">
                Customer management features are under development
              </Typography>
            </Card>
          </Grid>
        </Grid>
      </motion.div>
    </Box>
  );
};

export default CustomersPage;