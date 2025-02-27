import { createContext, useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import Loader from 'ui-component/Loader';

const AdminContext = createContext({});

export const useAdmin = () => useContext(AdminContext);

export const AdminProvider = ({ children }) => {
    const { user, loading } = useAuth();
    
    if (loading) {
        return <Loader message="Checking permissions..." />;
    }

    if (!user || user.is_admin !== 'admin') {
        return <Navigate to="/dashboard/default" replace />;
    }

    return (
        <AdminContext.Provider value={{ isAdmin: true }}>
            {children}
        </AdminContext.Provider>
    );
};

// Higher Order Component for admin-only routes
export const withAdmin = (Component) => {
    return function AdminComponent(props) {
        const { user } = useAuth();
        
        if (!user || user.is_admin !== 'admin') {
            return null;
        }

        return <Component {...props} />;
    };
};