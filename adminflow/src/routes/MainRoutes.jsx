import { lazy } from 'react';

// project imports
import MainLayout from 'layout/MainLayout';
import Loadable from 'ui-component/Loadable';
import { AdminProvider } from 'contexts/AdminContext';

// dashboard routing
const DashboardDefault = Loadable(lazy(() => import('views/dashboard/Default')));

// utilities routing
const UtilsTypography = Loadable(lazy(() => import('views/utilities/Typography')));
const UtilsColor = Loadable(lazy(() => import('views/utilities/Color')));
const UtilsShadow = Loadable(lazy(() => import('views/utilities/Shadow')));

// sample page routing
const SamplePage = Loadable(lazy(() => import('views/sample-page')));

// users page routing
const UserRegister = Loadable(lazy(() => import('views/user-control/UserRegister')));
const ManageUser = Loadable(lazy(() => import('views/user-control/ManageUser')));
const AreaDistribution = Loadable(lazy(() => import('views/user-control/AreaDistribution')));

// ==============================|| MAIN ROUTING ||============================== //

const MainRoutes = {
  path: '/',
  element: <MainLayout />,
  children: [
    {
      path: '/',
      element: <DashboardDefault />
    },
    {
      path: 'dashboard/default',
      element: <DashboardDefault />
    },
    {
      path: 'typography',
      element: <UtilsTypography />
    },
    {
      path: 'color',
      element: <UtilsColor />
    },
    {
      path: 'shadow',
      element: <UtilsShadow />
    },
    {
      path: 'sample-page',
      element: <SamplePage />
    },
    // User Control Routes wrapped with AdminProvider
    {
      path: 'user-control/register',
      element: <AdminProvider><UserRegister /></AdminProvider>
    },
    {
      path: 'user-control/manage',
      element: <AdminProvider><ManageUser /></AdminProvider>
    },
    {
      path: 'user-control/area-distribution',
      element: <AdminProvider><AreaDistribution /></AdminProvider>
    }
  ]
};

export default MainRoutes;
