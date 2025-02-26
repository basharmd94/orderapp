import { useRouteError, isRouteErrorResponse } from 'react-router-dom';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import Typography from '@mui/material/Typography';

export default function ErrorBoundary() {
  const error = useRouteError();

  let errorMessage = 'An unexpected error occurred';
  let title = 'Error';

  if (isRouteErrorResponse(error)) {
    if (error.status === 401) {
      title = 'Unauthorized';
      errorMessage = 'You need to log in to access this page';
    } else if (error.status === 404) {
      title = 'Not Found';
      errorMessage = 'The page you are looking for does not exist';
    } else if (error.status === 503) {
      title = 'Service Unavailable';
      errorMessage = 'Our servers are currently unavailable. Please try again later';
    }
  } else if (error instanceof Error) {
    errorMessage = error.message;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        p: 3
      }}
    >
      <Typography variant="h4" gutterBottom>
        {title}
      </Typography>
      <Alert severity="error" sx={{ maxWidth: 600 }}>
        {errorMessage}
      </Alert>
    </Box>
  );
}