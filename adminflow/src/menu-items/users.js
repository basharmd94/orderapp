import { IconUsers, IconUserPlus, IconUserCheck, IconMap2, IconUserEdit } from '@tabler/icons-react';
import { useAuth } from 'contexts/AuthContext'; // Import useAuth

const icons = { 
  IconUsers, 
  IconUserPlus, 
  IconUserCheck, 
  IconMap2,
  IconUserEdit
};

// Create the menu configuration
const getUsersMenu = () => {
  const { user } = useAuth();
  
  // Only return the menu if user is admin
  if (user?.is_admin === 'admin') {
    return {
      id: 'user-control',
      key: 'user-control',
      title: 'User Control',
      type: 'group',
      children: [
        {
          id: 'user-management',
          key: 'user-management',
          title: 'User Management',
          type: 'collapse',
          icon: icons.IconUsers,
          children: [
            {
              id: 'user-register',
              key: 'user-register',
              title: 'User Registration',
              type: 'item',
              url: '/user-control/register',
              icon: icons.IconUserPlus,              breadcrumbs: false
            },
            {
              id: 'manage-users',
              key: 'manage-users',
              title: 'Manage Users',
              type: 'item',
              url: '/user-control/manage',
              icon: icons.IconUserCheck,
              breadcrumbs: false
            },
            {
              id: 'area-distribution',
              key: 'area-distribution',
              title: 'Area Distribution',
              type: 'item',
              url: '/user-control/area-distribution',
              icon: icons.IconMap2,
              breadcrumbs: false
            }
          ]
        }
      ]
    };
  }
  
  return null; // Return null if user is not admin
};

export default getUsersMenu;