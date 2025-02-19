import React from 'react';
import {
  Modal,
  Box,
  Typography,
  IconButton,
  Grid,
  Chip,
  Divider,
  Paper,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled, keyframes } from '@mui/material/styles';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import InventoryIcon from '@mui/icons-material/Inventory';
import CategoryIcon from '@mui/icons-material/Category';
import InfoIcon from '@mui/icons-material/Info';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import DescriptionIcon from '@mui/icons-material/Description';
import ChatIcon from '@mui/icons-material/Chat';

const StyledModal = styled(Modal)({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  '& .MuiBackdrop-root': {
    backdropFilter: 'blur(8px)',
    backgroundColor: 'rgba(0, 0, 0, 0.5)', // Increased opacity for better contrast
    transition: 'opacity 0.3s ease-in-out',
  },
});

const ModalContent = styled(motion.div)(({ theme }) => ({
  position: 'relative',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 24,
  boxShadow: '0 12px 40px rgba(0,0,0,0.15)',
  padding: theme.spacing(4),
  maxWidth: 1000,
  width: '95%',
  maxHeight: '90vh',
  overflow: 'auto',
  opacity: 0,
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(2),
    width: '98%',
    borderRadius: 16,
    maxHeight: '95vh',
  },
  '&::-webkit-scrollbar': {
    width: '8px',
  },
  '&::-webkit-scrollbar-track': {
    background: '#f1f1f1',
    borderRadius: '4px',
  },
  '&::-webkit-scrollbar-thumb': {
    background: '#888',
    borderRadius: '4px',
    '&:hover': {
      background: '#555',
    },
  },
}));

const gradientAnimation = keyframes`
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
`;

const InfoCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  borderRadius: 16,
  background: theme.palette.background.paper,
  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '4px',
    background: `linear-gradient(45deg, 
      ${theme.palette.primary.main}, 
      ${theme.palette.secondary.main}, 
      ${theme.palette.primary.main})`,
    backgroundSize: '200% 200%',
    opacity: 0,
    transition: 'opacity 0.3s ease',
  },
  '&:hover': {
    transform: 'translateY(-4px) scale(1.01)',
    boxShadow: '0 12px 28px rgba(0,0,0,0.12)',
    '&::before': {
      opacity: 1,
      animation: `${gradientAnimation} 3s ease infinite`,
    },
    '& .icon': {
      transform: 'scale(1.1) rotate(5deg)',
      background: `linear-gradient(135deg, ${theme.palette.primary.light}, ${theme.palette.primary.main})`,
      color: theme.palette.common.white,
    },
  },
  '& .icon': {
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  }
}));

const CategoryTitle = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1.5),
  marginBottom: theme.spacing(2),
  '& .icon': {
    color: theme.palette.primary.main,
    background: theme.palette.primary.lighter,
    padding: theme.spacing(1.2), // Increased padding for larger icons
    borderRadius: 8,
    fontSize: '2rem', // Increased icon size
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  },
  '&:hover .icon': {
    transform: 'scale(1.1) rotate(5deg)',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
}));

const CloseButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  right: theme.spacing(2.5),
  top: theme.spacing(2.5),
  color: theme.palette.grey[700],
  background: theme.palette.background.paper,
  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
  transition: 'all 0.2s ease-in-out',
  padding: theme.spacing(1),
  '&:hover': {
    transform: 'rotate(90deg)',
    background: theme.palette.error.lighter,
    color: theme.palette.error.main,
    boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
  },
  '& .MuiSvgIcon-root': {
    fontSize: '1.5rem',
  },
}));

const DetailChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  padding: theme.spacing(1.2),
  height: 42, // Increased height more
  borderRadius: '10px',
  '& .MuiChip-label': {
    fontWeight: 600,
    fontSize: '1.1rem', // Increased font size
    padding: '0 16px',
  },
  '& .MuiChip-icon': {
    fontSize: '1.6rem', // Increased icon size more
    marginLeft: '8px',
  },
  boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 6px 16px rgba(0,0,0,0.16)',
  },
  '&.critical': {
    animation: 'pulse 2s infinite',
    background: theme.palette.error.light,
    color: theme.palette.error.contrastText,
    borderColor: theme.palette.error.main,
    '& .MuiChip-icon': {
      color: theme.palette.error.contrastText,
    },
  },
  '&.warning': {
    background: theme.palette.warning.light,
    color: theme.palette.warning.contrastText,
    borderColor: theme.palette.warning.main,
    '& .MuiChip-icon': {
      color: theme.palette.warning.contrastText,
    },
  },
  '@keyframes pulse': {
    '0%': {
      boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.6)', // Increased opacity
    },
    '70%': {
      boxShadow: '0 0 0 12px rgba(239, 68, 68, 0)', // Increased pulse size
    },
    '100%': {
      boxShadow: '0 0 0 0 rgba(239, 68, 68, 0)',
    },
  },
}));

const StockChip = styled(DetailChip)(({ theme, stockLevel }) => ({
  ...(stockLevel <= 5 && {
    background: `linear-gradient(135deg, ${theme.palette.error.main}, ${theme.palette.error.dark})`,
    color: theme.palette.error.contrastText,
    animation: 'pulse 2s infinite',
    '& .MuiChip-icon': {
      color: theme.palette.error.contrastText,
    },
  }),
  ...(stockLevel > 5 && stockLevel <= 10 && {
    background: `linear-gradient(135deg, ${theme.palette.warning.main}, ${theme.palette.warning.dark})`,
    color: theme.palette.warning.contrastText,
    '& .MuiChip-icon': {
      color: theme.palette.warning.contrastText,
    },
  }),
  ...(stockLevel > 10 && {
    background: `linear-gradient(135deg, ${theme.palette.success.main}, ${theme.palette.success.dark})`,
    color: theme.palette.success.contrastText,
    '& .MuiChip-icon': {
      color: theme.palette.success.contrastText,
    },
  }),
}));

const GlowingIconWrapper = styled(Box)(({ theme }) => ({
  width: 90,
  height: 90,
  borderRadius: '24px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: (theme) => `linear-gradient(135deg, ${theme.palette.primary.lighter}, ${theme.palette.primary.light})`,
  boxShadow: `0 8px 16px rgba(0,0,0,0.1),
              0 0 0 2px ${theme.palette.primary.main}20,
              0 0 20px ${theme.palette.primary.main}40`,
  animation: 'glow 3s ease-in-out infinite',
  '@keyframes glow': {
    '0%': {
      boxShadow: `0 8px 16px rgba(0,0,0,0.1),
                  0 0 0 2px ${theme.palette.primary.main}20,
                  0 0 20px ${theme.palette.primary.main}40`,
    },
    '50%': {
      boxShadow: `0 8px 16px rgba(0,0,0,0.1),
                  0 0 0 3px ${theme.palette.primary.main}30,
                  0 0 30px ${theme.palette.primary.main}60`,
    },
    '100%': {
      boxShadow: `0 8px 16px rgba(0,0,0,0.1),
                  0 0 0 2px ${theme.palette.primary.main}20,
                  0 0 20px ${theme.palette.primary.main}40`,
    },
  },
}));

const DetailSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2.5),
  background: theme.palette.background.default,
  borderRadius: theme.spacing(2),
  border: '1px solid',
  borderColor: theme.palette.divider,
  position: 'relative',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&::after': {
    content: '""',
    position: 'absolute',
    inset: 0,
    borderRadius: theme.spacing(2),
    padding: '2px',
    background: `linear-gradient(45deg, 
      ${theme.palette.primary.light}, 
      ${theme.palette.primary.main})`,
    WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
    WebkitMaskComposite: 'xor',
    maskComposite: 'exclude',
    opacity: 0,
    transition: 'opacity 0.3s ease',
  },
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
    '&::after': {
      opacity: 1,
    }
  }
}));

const SmallDetailChip = styled(DetailChip)(({ theme }) => ({
  height: 32,
  padding: theme.spacing(0.8),
  '& .MuiChip-label': {
    fontSize: '0.9rem',
    padding: '0 12px',
  },
  '& .MuiChip-icon': {
    fontSize: '1.2rem',
    marginLeft: '6px',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  },
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'translateY(-2px) scale(1.05)',
    boxShadow: '0 6px 16px rgba(0,0,0,0.15)',
    '& .MuiChip-icon': {
      transform: 'rotate(10deg) scale(1.1)',
    }
  }
}));

const AnimatedInfoCard = styled(InfoCard)(({ theme }) => ({
  overflow: 'hidden',
  position: 'relative',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(45deg, rgba(255,255,255,0) 40%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 60%)',
    zIndex: 1,
    transform: 'translateX(-100%)',
    transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
  },
  '&:hover': {
    transform: 'translateY(-4px) scale(1.01)',
    boxShadow: '0 12px 28px rgba(0,0,0,0.12)',
    '&::after': {
      transform: 'translateX(100%)',
    },
  },
}));

const SmallCategoryTitle = styled(CategoryTitle)(({ theme }) => ({
  marginBottom: theme.spacing(1.5),
  '& .icon': {
    padding: theme.spacing(0.8),
    fontSize: '1.5rem',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  },
  '& .MuiTypography-root': {
    fontSize: '1.1rem',
  },
  '&:hover .icon': {
    transform: 'scale(1.1) rotate(5deg)',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  }
}));

const PricingGrid = styled(Grid)(({ theme }) => ({
  '& .pricing-chip': {
    width: '100%',
    justifyContent: 'flex-start',
    height: 'auto',
    padding: theme.spacing(1.5),
    '& .MuiChip-label': {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
      gap: '4px',
    },
  },
}));

const PriceLabel = styled(Typography)({
  fontSize: '1.25rem',
  fontWeight: 700,
  display: 'block',
});

const PriceSubLabel = styled(Typography)({
  fontSize: '0.75rem',
  opacity: 0.8,
});

const modalVariants = {
  hidden: { 
    opacity: 0, 
    scale: 0.95,
    y: 20
  },
  visible: { 
    opacity: 1, 
    scale: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 25,
      duration: 0.3,
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.95,
    y: 20,
    transition: {
      duration: 0.2
    }
  }
};

const contentVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { 
      duration: 0.4,
      ease: "easeOut"
    }
  }
};

const pulseAnimation = keyframes`
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 255, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
`;

const PricingChip = styled(SmallDetailChip)(({ theme }) => ({
  width: '100%',
  height: 'auto',
  padding: theme.spacing(2),
  borderRadius: theme.spacing(2),
  flexDirection: 'column',
  alignItems: 'flex-start',
  gap: theme.spacing(0.5),
  '& .MuiChip-label': {
    padding: 0,
    width: '100%',
  },
  '& .MuiChip-icon': {
    margin: 0,
    marginBottom: theme.spacing(1),
    fontSize: '1.8rem',
  },
  '&.discount-active': {
    position: 'relative',
    '&::after': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      borderRadius: theme.spacing(2),
      animation: `${pulseAnimation} 2s infinite`,
    }
  }
}));

const ItemDetailsModal = ({ open, onClose, item }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  if (!item) return null;

  const formatPrice = (price) => {
    const formattedPrice = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'BDT',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
    return formattedPrice.replace('BDT', '৳');
  };

  const getStockColor = (stock) => {
    if (stock <= 5) return 'error';
    if (stock <= 10) return 'warning';
    return 'success';
  };

  const getStockText = (stock) => {
    if (stock <= 5) return 'Critical Stock';
    if (stock <= 10) return 'Low Stock';
    return 'In Stock';
  };

  return (
    <StyledModal
      open={open}
      onClose={onClose}
      closeAfterTransition
      BackdropProps={{
        timeout: 500,
      }}
    >
      <AnimatePresence mode="wait">
        {open && (
          <ModalContent
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <CloseButton 
              onClick={onClose} 
              aria-label="close"
              component={motion.button}
              whileHover={{ 
                rotate: 90,
                backgroundColor: theme.palette.error.lighter,
                color: theme.palette.error.main,
              }}
              whileTap={{ scale: 0.95 }}
            >
              <CloseIcon />
            </CloseButton>

            <motion.div variants={contentVariants}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 4, 
                gap: isMobile ? 2 : 3,
                p: isMobile ? 1.5 : 2,
                borderRadius: 3,
                flexDirection: isMobile ? 'column' : 'row',
                textAlign: isMobile ? 'center' : 'left',
                background: (theme) => `linear-gradient(to right, ${theme.palette.background.paper}, ${theme.palette.primary.lighter}15)`,
              }}>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring" }}
                >
                  <GlowingIconWrapper sx={{ width: isMobile ? 70 : 90, height: isMobile ? 70 : 90 }}>
                    <InventoryIcon sx={{ fontSize: isMobile ? 35 : 45, color: 'primary.main' }} />
                  </GlowingIconWrapper>
                </motion.div>

                <Box>
                  <Typography
                    variant={isMobile ? "h4" : "h3"}
                    sx={{ 
                      fontWeight: 700,
                      mb: 1,
                      background: (theme) => `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      textShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    }}
                  >
                    {item.item_name}
                  </Typography>
                  <DetailChip 
                    icon={<LocalOfferIcon sx={{ fontSize: isMobile ? 18 : 20 }} />}
                    label={formatPrice(item.std_price)}
                    color="primary"
                    sx={{ 
                      fontWeight: 600,
                      background: (theme) => theme.palette.primary.main,
                      color: 'white',
                      '& .MuiSvgIcon-root': {
                        color: 'white',
                      },
                    }}
                  />
                </Box>
              </Box>
            </motion.div>

            <Divider sx={{ my: 4 }} />

            <Grid container spacing={isMobile ? 2 : 3}>
              <Grid item xs={12} md={6}>
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <AnimatedInfoCard>
                    <CategoryTitle>
                      <InfoIcon className="icon" />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Basic Information
                      </Typography>
                    </CategoryTitle>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <StockChip 
                          icon={<InventoryIcon />}
                          label={`Stock: ${item.stock}`}
                          stockLevel={item.stock}
                          sx={{ m: 0.5 }}
                        />
                        <DetailChip 
                          icon={<CategoryIcon />}
                          label={`Group: ${item.item_group}`}
                          sx={{ 
                            m: 0.5,
                            background: (theme) => `linear-gradient(135deg, ${theme.palette.primary.light}, ${theme.palette.primary.main})`,
                            color: 'white',
                            '& .MuiChip-icon': {
                              color: 'white',
                            },
                          }}
                        />
                        <DetailChip 
                          icon={<InfoIcon />}
                          label={`ID: ${item.item_id}`}
                          sx={{ 
                            m: 0.5,
                            background: (theme) => theme.palette.grey[100],
                            border: '2px solid',
                            borderColor: 'divider',
                          }}
                        />
                      </Grid>
                    </Grid>
                  </AnimatedInfoCard>
                </motion.div>
              </Grid>

              <Grid item xs={12} md={6}>
                <motion.div
                  initial={{ x: 20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  <AnimatedInfoCard 
                    sx={{
                      borderLeft: '4px solid',
                      borderColor: (theme) => 
                        item.stock <= 5 ? theme.palette.error.main :
                        item.stock <= 10 ? theme.palette.warning.main :
                        theme.palette.success.main,
                    }}
                  >
                    <CategoryTitle>
                      <LocalShippingIcon className="icon" />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Stock Information
                      </Typography>
                    </CategoryTitle>
                    <Typography 
                      variant="h5" 
                      color={item.stock <= 10 ? getStockColor(item.stock) + '.main' : 'text.secondary'} 
                      paragraph
                      sx={{ 
                        fontWeight: 700,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                      }}
                    >
                      <InventoryIcon sx={{ fontSize: '2rem' }} />
                      {item.stock} units
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <StockChip 
                        label={getStockText(item.stock)}
                        stockLevel={item.stock}
                        sx={{ 
                          fontSize: '1.1rem',
                          height: 40,
                          '& .MuiChip-label': {
                            px: 3,
                            py: 0.5,
                            fontWeight: 700,
                          }
                        }}
                      />
                    </Box>
                  </AnimatedInfoCard>
                </motion.div>
              </Grid>

              <Grid item xs={12}>
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.45 }}
                >
                  <InfoCard>
                    <SmallCategoryTitle>
                      <LocalOfferIcon className="icon" />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Pricing & Discounts
                      </Typography>
                    </SmallCategoryTitle>

                    <PricingGrid container spacing={2}>
                      <Grid item xs={12} sm={4}>
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <PricingChip
                            icon={<LocalOfferIcon />}
                            label={
                              <Box>
                                <PriceLabel>{formatPrice(item.std_price)}</PriceLabel>
                                <PriceSubLabel>Standard Price</PriceSubLabel>
                              </Box>
                            }
                            sx={{
                              background: (theme) => `linear-gradient(135deg, ${theme.palette.success.light}, ${theme.palette.success.main})`,
                              color: 'white',
                              '& .MuiChip-icon': {
                                color: 'white',
                                fontSize: '1.5rem',
                              },
                            }}
                          />
                        </motion.div>
                      </Grid>

                      <Grid item xs={12} sm={4}>
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <PricingChip
                            icon={<InfoIcon />}
                            label={
                              <Box>
                                <PriceLabel>{item.min_disc_qty || 0}</PriceLabel>
                                <PriceSubLabel>Min. Quantity for Discount</PriceSubLabel>
                              </Box>
                            }
                            className={item.min_disc_qty > 0 ? 'discount-active' : ''}
                            sx={{
                              background: (theme) => `linear-gradient(135deg, ${theme.palette.info.light}, ${theme.palette.info.main})`,
                              color: 'white',
                              '& .MuiChip-icon': {
                                color: 'white',
                                fontSize: '1.5rem',
                              },
                            }}
                          />
                        </motion.div>
                      </Grid>

                      <Grid item xs={12} sm={4}>
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <PricingChip
                            icon={<LocalOfferIcon />}
                            label={
                              <Box>
                                <PriceLabel>{formatPrice(item.disc_amt || 0)}</PriceLabel>
                                <PriceSubLabel>Discount Amount</PriceSubLabel>
                              </Box>
                            }
                            className={item.disc_amt > 0 ? 'discount-active' : ''}
                            sx={{
                              background: (theme) => `linear-gradient(135deg, ${theme.palette.warning.light}, ${theme.palette.warning.main})`,
                              color: 'white',
                              '& .MuiChip-icon': {
                                color: 'white',
                                fontSize: '1.5rem',
                              },
                            }}
                          />
                        </motion.div>
                      </Grid>
                    </PricingGrid>

                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5 }}
                    >
                      <Box 
                        sx={{ 
                          mt: 3, 
                          p: 2, 
                          bgcolor: 'background.default', 
                          borderRadius: 2,
                          border: '1px dashed',
                          borderColor: 'divider',
                        }}
                      >
                        <motion.div
                          whileHover={{ scale: 1.01 }}
                          transition={{ type: "spring", stiffness: 400, damping: 10 }}
                        >
                          <Typography 
                            variant="subtitle2" 
                            color="text.secondary" 
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              gap: 1,
                              fontStyle: 'italic'
                            }}
                          >
                            <InfoIcon sx={{ fontSize: '1rem', color: 'primary.main' }} />
                            {item.min_disc_qty > 0 
                              ? `Bulk discount of ${formatPrice(item.disc_amt)} applies when ordering ${item.min_disc_qty} or more units`
                              : "No bulk discount available for this item"}
                          </Typography>
                        </motion.div>
                      </Box>
                    </motion.div>
                  </InfoCard>
                </motion.div>
              </Grid>


            </Grid>
          </ModalContent>
        )}
      </AnimatePresence>
    </StyledModal>
  );
};

export default ItemDetailsModal;