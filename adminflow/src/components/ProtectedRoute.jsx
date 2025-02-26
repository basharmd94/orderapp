import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Loader from 'ui-component/Loader';

const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    
    if (loading) {
        return <Loader message="Authenticating..." />;
    }

    if (!user) {
        return <Navigate to="/pages/login" replace />;
    }

    return children;
};

export default ProtectedRoute;