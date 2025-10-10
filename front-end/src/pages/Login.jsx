import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../components/AuthContext';

const Login = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = () => {
    login();                  // sets isAuthenticated = true
    navigate('/dashboard');   // redirect to dashboard after login
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '100px' }}>
      <h1>Login Page</h1>
      <button
        onClick={handleLogin}
        style={{
          padding: '10px 20px',
          marginTop: '20px',
          fontSize: '16px',
          cursor: 'pointer'
        }}
      >
        Login
      </button>
    </div>
  );
};

export default Login;
