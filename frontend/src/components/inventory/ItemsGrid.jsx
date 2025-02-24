import React, { useCallback, useRef, useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Chip,
  CardActions,
  Tooltip,
  Paper,
  Zoom,
  Fab,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import InventoryIcon from '@mui/icons-material/Inventory';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { motion } from 'framer-motion';
import ItemDetailsModal from './ItemDetailsModal';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  position: 'relative',
  overflow: 'visible',
  backgroundColor: theme.palette.background.paper,
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 12px 24px rgba(0,0,0,0.1)',
    '& .card-actions': {
      opacity: 1,
      transform: 'translateY(0)',
    },
  },
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '4px',
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
    borderTopLeftRadius: theme.shape.borderRadius,
    borderTopRightRadius: theme.shape.borderRadius,
  },
}));

const ItemIcon = styled(Box)(({ theme }) => ({
  width: 50,
  height: 50,
  borderRadius: '12px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: `linear-gradient(135deg, ${theme.palette.primary.lighter}, ${theme.palette.primary.light})`,
  color: theme.palette.primary.main,
  marginBottom: theme.spacing(2),
  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
}));

const PriceChip = styled(Paper)(({ theme }) => ({
  position: 'absolute',
  top: 16,
  right: 16,
  padding: '2px 6px',
  borderRadius: '4px',
  background: theme.palette.background.paper,
  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  display: 'inline-flex',
  alignItems: 'center',
  gap: '3px',
  border: `1px solid ${theme.palette.divider}`,
  transform: 'translateZ(0)',
  backfaceVisibility: 'hidden',
  willChange: 'transform',
  '&:hover': {
    transform: 'translateZ(0) scale(1.02)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.08)',
    borderColor: theme.palette.primary.light,
    '& .MuiSvgIcon-root': {
      transform: 'rotate(-12deg)',
      color: theme.palette.primary.main,
    },
    '& .price-text': {
      color: theme.palette.primary.main,
    }
  },
  transition: theme.transitions.create(['transform', 'box-shadow', 'border-color'], {
    duration: 200,
    easing: theme.transitions.easing.easeInOut,
  }),
}));

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
    y: 20
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 12
    }
  }
};

const ItemsGrid = ({ items, loading, hasMore, onLoadMore }) => {
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const observer = useRef();
  
  const lastItemRef = useCallback((node) => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        onLoadMore();
      }
    });
    
    if (node) observer.current.observe(node);
  }, [loading, hasMore, onLoadMore]);

  const formatPrice = (price) => {
    const formattedPrice = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'BDT',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
    
    return formattedPrice.replace('BDT', '৳'); // Using Bengali Taka symbol
  };

  const handleItemClick = (item, event) => {
    // Stop event propagation to prevent conflicts with other click handlers
    event.stopPropagation();
    setSelectedItem(item);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedItem(null);
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Grid container spacing={3}>
        {items.map((item, index) => (
          <Grid 
            item 
            xs={12} 
            sm={6} 
            md={4} 
            lg={3} 
            key={`${item.item_id}-${index}`}
            ref={index === items.length - 1 ? lastItemRef : null}
          >
            <motion.div variants={itemVariants}>
              <StyledCard>
                <CardContent 
                  onClick={(e) => handleItemClick(item, e)}
                  sx={{ 
                    flexGrow: 1, 
                    p: 3, 
                    pt: 4,
                    cursor: 'pointer',
                    '&:hover': {
                      '& .card-icon': {
                        transform: 'scale(1.1)',
                      }
                    }
                  }}
                >
                  <ItemIcon className="card-icon" sx={{ transition: 'transform 0.2s ease' }}>
                    <InventoryIcon sx={{ fontSize: 28 }} />
                  </ItemIcon>
                  
                  <PriceChip elevation={0} className="price-tag-shimmer">
                    <LocalOfferIcon sx={{ 
                      fontSize: 12,
                      color: 'text.secondary',
                      transition: 'transform 0.2s ease',
                    }} />
                    <Typography 
                      className="price-text"
                      variant="body2" 
                      color="text.primary" 
                      sx={{ 
                        fontWeight: 600,
                        fontSize: '0.75rem',
                        letterSpacing: '0.15px',
                        transition: 'color 0.2s ease',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '2px'
                      }}
                    >
                      {formatPrice(item.std_price)}
                    </Typography>
                  </PriceChip>

                  <Typography 
                    gutterBottom 
                    variant="h6" 
                    component="h2" 
                    noWrap
                    sx={{ 
                      fontWeight: 600,
                      mb: 1,
                      fontSize: '1.1rem',
                      lineHeight: 1.4,
                    }}
                  >
                    {item.item_name}
                  </Typography>
                  
                  <Typography 
                    variant="subtitle2" 
                    color="text.secondary" 
                    sx={{ mb: 2, opacity: 0.8 }}
                  >
                    ID: {item.item_id}
                  </Typography>

                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                    <Chip 
                      label={`Stock: ${item.stock}`}
                      size="small"
                      color={item.stock > 10 ? "success" : "warning"}
                      sx={{ 
                        fontWeight: 500,
                        '& .MuiChip-label': { px: 2 },
                      }}
                    />
                    <Chip 
                      label={item.item_group}
                      size="small"
                      variant="outlined"
                      sx={{ 
                        fontWeight: 500,
                        '& .MuiChip-label': { px: 2 },
                      }}
                    />
                  </Box>
                </CardContent>

                <CardActions 
                  className="card-actions"
                  onClick={(e) => e.stopPropagation()} // Prevent modal from opening when clicking actions
                  sx={{ 
                    justifyContent: 'flex-end', 
                    p: 2,
                    pt: 0,
                    opacity: 0,
                    transform: 'translateY(10px)',
                    transition: 'all 0.3s ease-in-out',
                  }}
                >
                  <Tooltip title="Edit Item">
                    <IconButton 
                      size="small" 
                      color="primary"
                      sx={{ 
                        bgcolor: 'primary.lighter',
                        '&:hover': { bgcolor: 'primary.light' },
                      }}
                    >
                      <EditIcon sx={{ fontSize: 20 }} />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete Item">
                    <IconButton 
                      size="small" 
                      color="error"
                      sx={{ 
                        bgcolor: 'error.lighter',
                        '&:hover': { bgcolor: 'error.light' },
                      }}
                    >
                      <DeleteIcon sx={{ fontSize: 20 }} />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </StyledCard>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <ItemDetailsModal 
        open={modalOpen}
        onClose={handleCloseModal}
        item={selectedItem}
      />
      
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Typography variant="body2" color="text.secondary">
              Loading more items...
            </Typography>
          </motion.div>
        </Box>
      )}
      
      {!hasMore && items.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <Typography variant="body2" color="text.secondary">
            No more items to load
          </Typography>
        </Box>
      )}
      
      {!loading && items.length === 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No items found
          </Typography>
        </Box>
      )}
    </motion.div>
  );
};

export default ItemsGrid;