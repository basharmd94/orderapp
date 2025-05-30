import { RouterProvider } from 'react-router-dom';
import { SnackbarProvider } from 'notistack';

// routing
import router from 'routes';

// project imports
import NavigationScroll from 'layout/NavigationScroll';
import ThemeCustomization from 'themes';

// auth provider
import { AuthProvider } from 'contexts/AuthContext';

// ==============================|| APP ||============================== //

export default function App() {
  return (
    <ThemeCustomization>
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <AuthProvider>
          <NavigationScroll>
            <>
              <RouterProvider router={router} />
            </>
          </NavigationScroll>
        </AuthProvider>
      </SnackbarProvider>
    </ThemeCustomization>
  );
}
