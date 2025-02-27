import { Navigate } from 'react-router-dom';
import { useAuth } from 'contexts/AuthContext';
import Loader from 'ui-component/Loader';

export default function RootRedirect() {
    const { user, loading } = useAuth();
    
    if (loading) {
        return <Loader message="Checking authentication..." />;
    }

    return user ? (
        <Navigate to="/dashboard/default" replace />
    ) : (
        <Navigate to="/pages/login" replace />
    );
}