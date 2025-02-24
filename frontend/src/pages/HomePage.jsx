import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import { 
  Box, 
  Typography, 
  Grid,
  Container,
} from '@mui/material';
import ErrorBoundary from '../components/common/ErrorBoundary';
import DashboardStats from '../components/dashboard/DashboardStats';
import RecentActivity from '../components/dashboard/RecentActivity';

const HomePage = () => {
  const { user } = useAuth();

  return (
    <Box 
      component="main" 
      sx={{ 
        flexGrow: 1,
        py: 3,
        px: { xs: 2, md: 4 },
        width: '100%',
        maxWidth: '100%',
        overflowX: 'hidden'
      }}
    >
      <Container maxWidth={false}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography 
            variant="h4" 
            sx={{ 
              mb: 5,
              fontWeight: 600,
              color: 'text.primary',
            }}
          >
            Welcome back, {user?.user_name}
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <ErrorBoundary>
                <DashboardStats />
              </ErrorBoundary>
            </Grid>

            <Grid item xs={12}>
              <ErrorBoundary>
                <RecentActivity />
              </ErrorBoundary>
            </Grid>
          </Grid>
        </motion.div>
      </Container>
    </Box>
  );
};

export default HomePage;