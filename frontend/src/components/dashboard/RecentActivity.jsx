import React from 'react';
import {
  Card,
  Typography,
  Box,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import InventoryIcon from '@mui/icons-material/Inventory';

const ActivityCard = styled(Card)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  overflow: 'hidden',
}));

const TimelineConnector = styled('div')(({ theme }) => ({
  position: 'absolute',
  left: 36,  // Centered with the avatar
  top: 0,
  bottom: 0,
  width: 2,
  backgroundColor: theme.palette.divider,
  transform: 'translateX(-50%)',  // Center the line
}));

const StyledListItem = styled(ListItem)(({ theme }) => ({
  position: 'relative',
  paddingLeft: theme.spacing(2),
  minHeight: 80,
  '&:hover': {
    backgroundColor: 'rgba(0, 0, 0, 0.02)',
  },
}));

const StyledAvatar = styled(Avatar)(({ theme }) => ({
  position: 'relative',
  zIndex: 2,  // Place avatar above the timeline
  border: `3px solid ${theme.palette.background.paper}`,  // Add border to make it stand out
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'scale(1.1)',
  },
}));

const activities = [
  {
    id: 1,
    type: 'order',
    title: 'New order received',
    description: 'Order #12345 from John Doe',
    time: '2 minutes ago',
    icon: <ShoppingCartIcon />,
    color: 'primary',
    status: 'New',
  },
  {
    id: 2,
    type: 'customer',
    title: 'New customer registered',
    description: 'Jane Smith created an account',
    time: '1 hour ago',
    icon: <PersonAddIcon />,
    color: 'success',
    status: 'Completed',
  },
  {
    id: 3,
    type: 'delivery',
    title: 'Order shipped',
    description: 'Order #12342 has been shipped',
    time: '2 hours ago',
    icon: <LocalShippingIcon />,
    color: 'info',
    status: 'In Transit',
  },
  {
    id: 4,
    type: 'inventory',
    title: 'Low stock alert',
    description: 'Item #789 is running low',
    time: '3 hours ago',
    icon: <InventoryIcon />,
    color: 'warning',
    status: 'Alert',
  },
];

const RecentActivity = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { 
      opacity: 0, 
      x: -20 
    },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 12
      }
    }
  };

  return (
    <ActivityCard>
      <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
        Recent Activity
      </Typography>

      <Box sx={{ position: 'relative' }}>
        <TimelineConnector />
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <List sx={{ position: 'relative', py: 0 }}>
            {activities.map((activity, index) => (
              <motion.div
                key={activity.id}
                variants={itemVariants}
              >
                <StyledListItem>
                  <ListItemAvatar>
                    <StyledAvatar
                      sx={{
                        bgcolor: `${activity.color}.light`,
                        color: `${activity.color}.main`,
                        boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
                      }}
                    >
                      {activity.icon}
                    </StyledAvatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                          {activity.title}
                        </Typography>
                        <Chip
                          label={activity.status}
                          size="small"
                          color={activity.color}
                          sx={{ 
                            height: 20,
                            fontWeight: 500,
                            fontSize: '0.75rem'
                          }}
                        />
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 0.5 }}>
                        <Typography 
                          variant="body2" 
                          color="text.secondary"
                          sx={{ mb: 0.5 }}
                        >
                          {activity.description}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ 
                            display: 'block',
                            opacity: 0.8
                          }}
                        >
                          {activity.time}
                        </Typography>
                      </Box>
                    }
                  />
                </StyledListItem>
                {index < activities.length - 1 && (
                  <Divider 
                    component="li" 
                    sx={{ 
                      ml: 7.25,
                      mr: 2,
                      opacity: 0.7
                    }} 
                  />
                )}
              </motion.div>
            ))}
          </List>
        </motion.div>
      </Box>
    </ActivityCard>
  );
};

export default RecentActivity;