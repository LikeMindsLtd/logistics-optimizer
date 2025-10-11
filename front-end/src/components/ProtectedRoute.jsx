import { useContext } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { AuthContext } from './AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useContext(AuthContext);
  const location = useLocation();

  // Allow access to public routes (login or 404) even if not authenticated
  const publicPaths = ['/login', '/404'];

  if (!isAuthenticated && !publicPaths.includes(location.pathname)) {
    // Redirect to login if trying to access a protected page
    return <Navigate to="/login" replace />;
  }

  // Otherwise render the requested page (dashboard, plants, etc.)
  return children;
};

export default ProtectedRoute;
