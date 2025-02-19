import React, { useEffect, useState } from 'react';
import { Fab } from '@mui/material';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme, useMediaQuery } from '@mui/material';

const ScrollToTop = () => {
  const [isVisible, setIsVisible] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  useEffect(() => {
    let timeoutId;
    
    const toggleVisibility = () => {
      const scrolled = Math.max(
        window.pageYOffset,
        document.documentElement.scrollTop,
        document.body.scrollTop
      );
      
      const threshold = Math.min(300, window.innerHeight * 0.3);
      
      // Clear any existing timeout
      clearTimeout(timeoutId);
      
      // Add a small delay to prevent flickering
      timeoutId = setTimeout(() => {
        setIsVisible(scrolled > threshold);
      }, 100);
    };

    window.addEventListener('scroll', toggleVisibility, { passive: true });
    toggleVisibility();

    return () => {
      window.removeEventListener('scroll', toggleVisibility);
      clearTimeout(timeoutId);
    };
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.5, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.5, y: 20 }}
          transition={{
            type: "spring",
            stiffness: 260,
            damping: 20,
            delay: 0.1 // Small delay for smoother appearance
          }}
          style={{
            position: 'fixed',
            top: isMobile ? '45%' : '90%',  // Position much higher
            right: isMobile ? '12px' : '90px',  // Slightly more to the left
            zIndex: 2000,
          }}
        >
          <Fab
            color="primary"
            size={isMobile ? "small" : "medium"}
            aria-label="scroll back to top"
            onClick={scrollToTop}
            className="scroll-top-button"
            sx={{
              opacity: 0.9,
              '&:hover': {
                opacity: 1,
                transform: 'translateY(-4px)',
              },
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          >
            <KeyboardArrowUpIcon fontSize={isMobile ? "small" : "medium"} />
          </Fab>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ScrollToTop;