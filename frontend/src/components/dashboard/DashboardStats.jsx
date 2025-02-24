import React from 'react';
import { 
  Grid, 
  Card, 
  Typography, 
  Box,
  IconButton,
  LinearProgress,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import PeopleIcon from '@mui/icons-material/People';
import InventoryIcon from '@mui/icons-material/Inventory';
import MoreVertIcon from '@mui/icons-material/MoreVert';

const StatsCard = styled(Card)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  minHeight: '180px',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  },
}));

const IconWrapper = styled(Box)(({ theme, color }) => ({
  width: 48,
  height: 48,
  borderRadius: '12px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: theme.palette[color].light,
  color: theme.palette[color].main,
  marginBottom: theme.spacing(2),
}));

const stats = [
  {
    title: 'Total Orders',
    value: '2,543',
    icon: <ShoppingCartIcon />,
    color: 'primary',
    trend: '+12%',
    progress: 75,
  },
  {
    title: 'Active Customers',
    value: '1,243',
    icon: <PeopleIcon />,
    color: 'success',
    trend: '+8%',
    progress: 65,
  },
  {
    title: 'Inventory Items',
    value: '856',
    icon: <InventoryIcon />,
    color: 'warning',
    trend: '+5%',
    progress: 85,
  },
  {
    title: 'Revenue Growth',
    value: '$42.5k',
    icon: <TrendingUpIcon />,
    color: 'info',
    trend: '+15%',
    progress: 70,
  },
];

const DashboardStats = () => {
  return (
    <Box sx={{ width: '100%', mb: 3 }}>
      <Grid container spacing={3}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} lg={3} key={index}>
            <StatsCard>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <IconWrapper color={stat.color}>
                  {stat.icon}
                </IconWrapper>
                <IconButton size="small">
                  <MoreVertIcon />
                </IconButton>
              </Box>
              
              <Typography variant="h4" sx={{ mb: 1, fontWeight: 'bold' }}>
                {stat.value}
              </Typography>
              
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                {stat.title}
              </Typography>
              
              <Box sx={{ mt: 'auto' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: stat.trend.startsWith('+') ? 'success.main' : 'error.main',
                      fontWeight: 'bold',
                      mr: 1
                    }}
                  >
                    {stat.trend}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    vs last month
                  </Typography>
                </Box>
                
                <LinearProgress 
                  variant="determinate" 
                  value={stat.progress} 
                  sx={{ 
                    height: 6,
                    borderRadius: 1,
                    backgroundColor: `${stat.color}.lighter`,
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 1,
                      backgroundColor: `${stat.color}.main`,
                    },
                  }} 
                />
              </Box>
            </StatsCard>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default DashboardStats;