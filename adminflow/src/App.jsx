import { RouterProvider } from 'react-router-dom';

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
      <AuthProvider>
        <NavigationScroll>
          <>
            <RouterProvider router={router} />
          </>
        </NavigationScroll>
      </AuthProvider>
    </ThemeCustomization>
  );
}
