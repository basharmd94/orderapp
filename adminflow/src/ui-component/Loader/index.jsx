import LinearProgress from '@mui/material/LinearProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

// ==============================|| LOADER ||============================== //

export default function Loader({ message = 'Loading...' }) {
  return (
    <Box sx={{ position: 'fixed', top: 0, left: 0, zIndex: 1301, width: '100%' }}>
      <LinearProgress color="primary" />
      <Box
        sx={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center'
        }}
      >
        <Typography variant="caption" color="textSecondary">
          {message}
        </Typography>
      </Box>
    </Box>
  );
}