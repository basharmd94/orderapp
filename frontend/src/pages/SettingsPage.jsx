import React from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  Switch,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Button
} from '@mui/material';
import { motion } from 'framer-motion';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SecurityIcon from '@mui/icons-material/Security';
import LanguageIcon from '@mui/icons-material/Language';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import StorageIcon from '@mui/icons-material/Storage';
import CachedIcon from '@mui/icons-material/Cached';
import { useAuth } from '../contexts/AuthContext';

const SettingsPage = () => {
  const { user } = useAuth();

  const settings = [
    {
      title: 'Notifications',
      icon: <NotificationsIcon />,
      description: 'Manage your notification preferences',
      value: true,
    },
    {
      title: 'Security',
      icon: <SecurityIcon />,
      description: 'Configure security settings and 2FA',
      value: true,
    },
    {
      title: 'Language',
      icon: <LanguageIcon />,
      description: 'Choose your preferred language',
      value: false,
    },
    {
      title: 'Dark Mode',
      icon: <DarkModeIcon />,
      description: 'Toggle dark/light theme',
      value: false,
    },
    {
      title: 'Cache',
      icon: <StorageIcon />,
      description: 'Manage application cache',
      value: true,
    },
    {
      title: 'Auto Update',
      icon: <CachedIcon />,
      description: 'Enable automatic updates',
      value: true,
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" sx={{ mb: 4, fontWeight: 600 }}>
          Settings
        </Typography>

        <Grid container spacing={3}>
          {/* User Profile Settings */}
          <Grid item xs={12} md={4}>
            <Card sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                User Profile
              </Typography>
              <List>
                <ListItem>
                  <ListItemText 
                    primary="Username"
                    secondary={user?.user_name}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Email"
                    secondary={user?.email || 'Not set'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Role"
                    secondary={user?.is_admin === 'admin' ? 'Administrator' : 'User'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Business ID"
                    secondary={user?.businessId}
                  />
                </ListItem>
              </List>
              <Button 
                variant="contained" 
                fullWidth 
                sx={{ mt: 2 }}
              >
                Edit Profile
              </Button>
            </Card>
          </Grid>

          {/* Application Settings */}
          <Grid item xs={12} md={8}>
            <Card sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Application Settings
              </Typography>
              <List>
                {settings.map((setting, index) => (
                  <React.Fragment key={setting.title}>
                    <ListItem>
                      <ListItemIcon>
                        {setting.icon}
                      </ListItemIcon>
                      <ListItemText 
                        primary={setting.title}
                        secondary={setting.description}
                      />
                      <ListItemSecondaryAction>
                        <Switch 
                          edge="end"
                          defaultChecked={setting.value}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < settings.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </Card>
          </Grid>

          {/* Advanced Settings (Admin Only) */}
          {user?.is_admin === 'admin' && (
            <Grid item xs={12}>
              <Card sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Advanced Settings
                </Typography>
                <Typography color="text.secondary" paragraph>
                  These settings are only available to administrators.
                </Typography>
                <Button 
                  variant="outlined" 
                  color="primary"
                  sx={{ mr: 2 }}
                >
                  System Configuration
                </Button>
                <Button 
                  variant="outlined" 
                  color="secondary"
                >
                  Manage Users
                </Button>
              </Card>
            </Grid>
          )}
        </Grid>
      </motion.div>
    </Box>
  );
};

export default SettingsPage;