import { createBrowserRouter } from 'react-router-dom';

// routes
import AuthenticationRoutes from './AuthenticationRoutes';
import MainRoutes from './MainRoutes';
import ProtectedRoute from 'components/ProtectedRoute';
import ErrorBoundary from 'components/ErrorBoundary';
import RootRedirect from 'components/RootRedirect';

// ==============================|| ROUTING RENDER ||============================== //

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootRedirect />,
    errorElement: <ErrorBoundary />
  },
  {
    ...MainRoutes,
    element: <ProtectedRoute>{MainRoutes.element}</ProtectedRoute>,
    errorElement: <ErrorBoundary />,
    children: MainRoutes.children.map(route => ({
      ...route,
      element: <ProtectedRoute>{route.element}</ProtectedRoute>,
      errorElement: <ErrorBoundary />
    }))
  },
  {
    ...AuthenticationRoutes,
    errorElement: <ErrorBoundary />
  }
], {
  basename: import.meta.env.VITE_APP_BASE_NAME
});

export default router;
