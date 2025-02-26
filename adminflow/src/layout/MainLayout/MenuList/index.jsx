import { memo, useState } from 'react';
import Divider from '@mui/material/Divider';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

// project imports
import NavItem from './NavItem';
import NavGroup from './NavGroup';
import menuItems from 'menu-items';

import { useGetMenuMaster } from 'api/menu';

// ==============================|| SIDEBAR MENU LIST ||============================== //

function MenuList() {
  const { menuMaster } = useGetMenuMaster();
  const drawerOpen = menuMaster.isDashboardDrawerOpened;
  const [selectedID, setSelectedID] = useState('');

  // Process the menu items
  const processedItems = menuItems.items
    .map(item => {
      // If item is a function, execute it to get dynamic menu
      if (typeof item === 'function') {
        return item();
      }
      return item;
    })
    .filter(Boolean); // Remove null/undefined items

  const navItems = processedItems.map((item, index) => {
    const key = item.key || item.id || `menu-item-${index}`;

    switch (item.type) {
      case 'group':
        if (item.url) {
          return (
            <List key={key}>
              <NavItem 
                item={item} 
                level={1} 
                isParents 
                setSelectedID={() => setSelectedID('')} 
              />
              {index !== 0 && <Divider sx={{ py: 0.5 }} />}
            </List>
          );
        }

        return (
          <NavGroup
            key={key}
            setSelectedID={setSelectedID}
            selectedID={selectedID}
            item={item}
          />
        );
      default:
        return (
          <Typography key={key} variant="h6" color="error" align="center">
            Menu Items Error
          </Typography>
        );
    }
  });

  return <Box {...(drawerOpen && { sx: { mt: 1.5 } })}>{navItems}</Box>;
}

export default memo(MenuList);
