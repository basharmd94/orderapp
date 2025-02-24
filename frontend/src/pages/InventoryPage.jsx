import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Tabs,
  Tab,
  TextField,
  InputAdornment,
} from '@mui/material';
import { motion } from 'framer-motion';
import SearchIcon from '@mui/icons-material/Search';
import apiClient from '../services/apiClient';
import ItemsGrid from '../components/inventory/ItemsGrid';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ScrollToTop from '../components/common/ScrollToTop';
import '../components/inventory/inventory.css';

const InventoryPage = () => {
  const [tabValue, setTabValue] = useState(0);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrolled = document.documentElement.scrollTop || document.body.scrollTop;
      const threshold = 400; // Show button after scrolling 400px
      setShowScrollTop(scrolled > threshold);
    };

    // Add passive event listener for better scroll performance
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    // Initial check in case page is already scrolled
    handleScroll();

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  const tabConfig = [
    { label: 'HMBR-Items', zid: 100001 },
    { label: 'GI-Items', zid: 100000 },
    { label: 'Zepto-Items', zid: 100005 },
  ];

  const fetchItems = async (reset = false) => {
    if (!hasMore && !reset) return;
    
    try {
      setLoading(true);
      const newPage = reset ? 0 : page;
      const currentZid = tabConfig[tabValue].zid;
      const searchParam = searchTerm ? `&item_name=${encodeURIComponent(searchTerm)}` : '';
      
      const response = await apiClient.get(
        `/items/all/${currentZid}?limit=10&offset=${newPage * 10}${searchParam}`
      );
      
      const newItems = response.data;
      if (newItems.length < 10) {
        setHasMore(false);
      }

      setItems(reset ? newItems : [...items, ...newItems]);
      if (!reset) {
        setPage(newPage + 1);
      }
    } catch (error) {
      console.error('Error fetching items:', error);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  };

  // Debounce search to avoid too many API calls
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setItems([]);
      setPage(0);
      setHasMore(true);
      fetchItems(true);
    }, 500);
    
    return () => clearTimeout(timeoutId);
  }, [tabValue, searchTerm]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleLoadMore = () => {
    if (!loading) {
      fetchItems();
    }
  };

  return (
    <Box sx={{ p: 0 }} className="inventory-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ px: 4, py: 3, mb: 2 }}>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            Inventory Management
          </Typography>
        </Box>

        <Box sx={{ width: '100%' }}>
          <div className="inventory-tabs">
            <Box sx={{ maxWidth: '1600px', mx: 'auto', width: '100%' }}>
              <Tabs 
                value={tabValue} 
                onChange={handleTabChange}
                variant="fullWidth"
                sx={{
                  mb: 3,
                  '& .MuiTab-root': {
                    fontWeight: 600,
                    fontSize: '1rem',
                    minHeight: '56px',
                    color: 'text.primary',
                    '&.Mui-selected': {
                      color: 'primary.main',
                    },
                    '&:hover': {
                      backgroundColor: 'primary.lighter',
                    },
                  },
                  '& .MuiTabs-indicator': {
                    height: '3px',
                    borderRadius: '2px',
                  },
                }}
              >
                {tabConfig.map((tab) => (
                  <Tab 
                    key={tab.zid} 
                    label={tab.label}
                  />
                ))}
              </Tabs>

              <TextField
                fullWidth
                variant="outlined"
                placeholder="Search items..."
                value={searchTerm}
                onChange={handleSearch}
                className="search-field"
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
          </div>

          <Box sx={{ maxWidth: '1600px', mx: 'auto', px: 4, pb: 4 }}>
            {loading && items.length === 0 ? (
              <LoadingSpinner message="Loading items..." />
            ) : (
              <ItemsGrid 
                items={items}
                loading={loading}
                hasMore={hasMore}
                onLoadMore={handleLoadMore}
              />
            )}
          </Box>
        </Box>

        <ScrollToTop />
      </motion.div>
    </Box>
  );
};

export default InventoryPage;