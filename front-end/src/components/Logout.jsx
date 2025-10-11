import { useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from './AuthContext';

export default function Logout() {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    // Perform logout
    logout();

    // Redirect to login page after logout
    navigate('/login', { replace: true });
  }, [logout, navigate]);

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <div className="bg-white p-6 rounded shadow-md text-center">
        <h2 className="text-xl font-semibold mb-2">Logging Out...</h2>
        <p className="text-gray-500">You will be redirected to the login page shortly.</p>
      </div>
    </div>
  );
}
